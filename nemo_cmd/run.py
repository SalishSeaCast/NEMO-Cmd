# Copyright 2013-2018 The Salish Sea MEOPAR Contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""NEMO-Cmd command plug-in for run sub-command.

Prepare for, execute, and gather the results of a run of the NEMO model.
"""
from __future__ import division

import datetime
import logging
import math
import time
import os
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import subprocess

import cliff.command

from nemo_cmd import api, lib
from nemo_cmd.fspath import fspath
from nemo_cmd.prepare import get_n_processors, get_run_desc_value

logger = logging.getLogger(__name__)


class Run(cliff.command.Command):
    """Prepare, execute, and gather results from a NEMO model run.
    """

    def get_parser(self, prog_name):
        parser = super(Run, self).get_parser(prog_name)
        parser.description = '''
            Prepare, execute, and gather the results from a NEMO
            run described in DESC_FILE.
            The results files from the run are gathered in RESULTS_DIR.

            If RESULTS_DIR does not exist it will be created.
        '''
        parser.add_argument(
            'desc_file',
            metavar='DESC_FILE',
            type=Path,
            help='run description YAML file'
        )
        parser.add_argument(
            'results_dir',
            metavar='RESULTS_DIR',
            help='directory to store results into'
        )
        parser.add_argument(
            '--max-deflate-jobs',
            dest='max_deflate_jobs',
            type=int,
            default=4,
            help='''
            Maximum number of concurrent sub-processes to
            use for netCDF deflating. Defaults to 4.'''
        )
        parser.add_argument(
            '--nocheck-initial-conditions',
            dest='nocheck_init',
            action='store_true',
            help='''
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to wait on a
            previous job'''
        )
        parser.add_argument(
            '--no-deflate',
            dest='no_deflate',
            action='store_true',
            help='''
            Do not include "nemo deflate" command in the bash script.
            Use this option if you are using on-the-fly deflation in XIOS-2;
            i.e. you are using 1 XIOS-2 process and have the 
            compression_level="4" attribute set in all of the file_group
            definitions in your file_def.xml file.            
            '''
        )
        parser.add_argument(
            '--no-submit',
            dest='no_submit',
            action='store_true',
            help='''
            Prepare the temporary run directory, and the bash script to execute
            the NEMO run, but don't submit the run to the queue.
            This is useful during development runs when you want to hack on the
            bash script and/or use the same temporary run directory more than
            once.
            '''
        )
        parser.add_argument(
            '--waitjob',
            type=int,
            default=0,
            help='''
            use -W waitjob in call to qsub, to make current job
            wait for on waitjob.  Waitjob is the queue job number
            '''
        )
        parser.add_argument(
            '--queue-job-cmd',
            dest='queue_job_cmd',
            type=str,
            choices={'qsub', 'sbatch'},
            default='qsub',
            help='''
            Command to use to submit the bash script to execute the NEMO run;
            defaults to qsub.
            '''
        )
        parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help="don't show the run directory path or job submission message"
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `nemo run` sub-coomand.

        The message generated upon submission of the run to the queue
        manager is logged to the console.

        :param parsed_args: Arguments and options parsed from the command-line.
        :type parsed_args: :class:`argparse.Namespace` instance
        """
        qsub_msg = run(
            parsed_args.desc_file,
            parsed_args.results_dir,
            parsed_args.max_deflate_jobs,
            parsed_args.nocheck_init,
            parsed_args.no_deflate,
            parsed_args.no_submit,
            parsed_args.waitjob,
            parsed_args.queue_job_cmd,
            quiet=parsed_args.quiet
        )
        if qsub_msg and not parsed_args.quiet:
            logger.info(qsub_msg)


def run(
    desc_file,
    results_dir,
    max_deflate_jobs=4,
    nocheck_init=False,
    no_deflate=False,
    no_submit=False,
    waitjob=0,
    queue_job_cmd='qsub',
    quiet=False
):
    """Create and populate a temporary run directory, and a run script,
    and submit the run to the queue manager.

    The temporary run directory is created and populated via the
    :func:`nemo_cmd.api.prepare` API function.
    The system-specific run script is stored in :file:`NEMO.sh`
    in the run directory.
    That script is submitted to the queue manager in a subprocess.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param str results_dir: Path of the directory in which to store the run
                            results;
                            it will be created if it does not exist.

    :param int max_deflate_jobs: Maximum number of concurrent sub-processes to
                                 use for netCDF deflating.

    :param boolean nocheck_init: Suppress initial condition link check
                                 the default is to check

    :param boolean no_deflate: Do not include "nemo deflate" command in
                               the bash script.

    :param boolean no_submit: Prepare the temporary run directory,
                              and the bash script to execute the NEMO run,
                              but don't submit the run to the queue.

    :param int waitjob: Use -W waitjob in call to qsub, to make current job
                        wait for on waitjob.  Waitjob is the queue job number

    :param str queue_job_cmd: Command to use to submit the bash script to
                              execute the NEMO run.

    :param boolean quiet: Don't show the run directory path message;
                          the default is to show the temporary run directory
                          path.

    :returns: Message generated by queue manager upon submission of the
              run script.
    :rtype: str
    """
    run_dir = api.prepare(desc_file, nocheck_init)
    if not quiet:
        logger.info('Created run directory {}'.format(run_dir))
    run_desc = lib.load_run_desc(desc_file)
    nemo_processors = get_n_processors(run_desc, run_dir)
    separate_xios_server = get_run_desc_value(
        run_desc, ('output', 'separate XIOS server')
    )
    xios_processors = get_run_desc_value(run_desc,
                                         ('output', 'XIOS servers'
                                          )) if separate_xios_server else 0
    results_dir = Path(results_dir)
    batch_script = _build_batch_script(
        run_desc, fspath(desc_file), nemo_processors, xios_processors,
        no_deflate, max_deflate_jobs, results_dir, run_dir, queue_job_cmd
    )
    batch_file = run_dir / 'NEMO.sh'
    with batch_file.open('wt') as f:
        f.write(batch_script)
    if no_submit:
        return
    starting_dir = Path.cwd()
    os.chdir(fspath(run_dir))
    if waitjob:
        ## TODO: This is qsub syntax that needs to be generalized
        ## for other queue managers such as slurm
        cmd = '{submit_job} -W depend=afterok:{waitjob} NEMO.sh'.format(
            submit_job=queue_job_cmd, waitjob=waitjob
        )
    else:
        cmd = '{submit_job} NEMO.sh'.format(submit_job=queue_job_cmd)
    results_dir.mkdir(parents=True, exist_ok=True)
    try:
        submit_job_msg = subprocess.check_output(
            cmd.split(), universal_newlines=True
        )
    except OSError:
        logger.error(
            '{submit_job} not found. Please confirm the correct job submission '
            'command (qsub or sbatch) for this platform and use the '
            '--job-queue-cmd command-line option.'.format(
                submit_job=queue_job_cmd
            )
        )
        # Remove the temporary run directory
        time.sleep(0.1)
        try:
            for p in run_dir.iterdir():
                p.unlink()
            run_dir.rmdir()
        except OSError:
            pass
        submit_job_msg = None
    os.chdir(fspath(starting_dir))
    return submit_job_msg


def _build_batch_script(
    run_desc, desc_file, nemo_processors, xios_processors, no_deflate,
    max_deflate_jobs, results_dir, run_dir, queue_job_cmd
):
    """Build the Bash script that will execute the run.

    :param no_deflate:
    :param dict run_desc: Run description dictionary.

    :param str desc_file: File path/name of the YAML run description file.

    :param int nemo_processors: Number of processors that NEMO will be executed
                                on.

    :param int xios_processors: Number of processors that XIOS will be executed
                                on.

    :param boolean no_deflate: Do not include "nemo deflate" command in
                               the bash script.

    :param int max_deflate_jobs: Maximum number of concurrent sub-processes to
                                 use for netCDF deflating.

    :param results_dir: Path of the directory in which to store the run
                        results;
                        it will be created if it does not exist.
    :type results_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param str queue_job_cmd: Command to use to submit the bash script to
                              execute the NEMO run.

    :returns: Bash script to execute the run.
    :rtype: str
    """
    script = u'#!/bin/bash\n'
    scheduler_directives = {
        'qsub': _pbs_directives,
        'sbatch': _sbatch_directives,
    }
    script = u'\n'.join((
        script, scheduler_directives[queue_job_cmd](
            run_desc, nemo_processors + xios_processors, results_dir
        )
    ))
    script = u'\n'.join((
        script, u'{defns}\n'.format(
            defns=_definitions(
                run_desc, desc_file, run_dir, results_dir, queue_job_cmd,
                no_deflate
            ),
        )
    ))
    if 'modules to load' in run_desc:
        script = u'\n'.join((
            script, u'{modules}\n'.format(
                modules=_modules(run_desc['modules to load']),
            )
        ))
    script = u'\n'.join((
        script, u'{execute}\n'
        u'{fix_permissions}\n'
        u'{cleanup}'.format(
            execute=_execute(
                nemo_processors, xios_processors, no_deflate, max_deflate_jobs
            ),
            fix_permissions=_fix_permissions(),
            cleanup=_cleanup(),
        )
    ))
    return script


def _pbs_directives(run_desc, n_processors, results_dir):
    email = get_run_desc_value(run_desc, ('email',))
    pbs_directives = u''.join((
        u'{pbs_common}\n'.format(
            pbs_common=api.
            pbs_common(run_desc, n_processors, email, results_dir)
        )
    ))
    if 'PBS resources' in run_desc:
        pbs_directives = u''.join((
            pbs_directives[:-1],
            '# resource(s) requested in run description YAML file\n'
        ))
        pbs_directives = u''.join((
            pbs_directives, u'{pbs_resources}\n'.format(
                pbs_resources=_pbs_resources(
                    run_desc['PBS resources'], n_processors
                )
            )
        ))
    return pbs_directives


def _pbs_resources(resources, n_processors):
    pbs_directives = u''
    for resource in resources:
        if 'nodes=' in resource and ':ppn=' in resource:
            _, ppn = resource.rsplit('=', 1)
            nodes = math.ceil(n_processors / int(ppn))
            resource = 'nodes={nodes}:ppn={ppn}'.format(
                nodes=int(nodes), ppn=ppn
            )
        pbs_directives = u''.join((
            pbs_directives, u'#PBS -l {resource}\n'.format(resource=resource)
        ))
    return pbs_directives


def _sbatch_directives(
    run_desc,
    n_processors,
    results_dir,
    max_tasks_per_node=32,
    memory_per_node='125G'
):
    """Return the SBATCH directives used to run NEMO on a cluster that uses the
    Slurm Workload Manager for job scheduling.

    The strategy for requesting compute resources is to request full nodes
    (all processors and all memory) so that XIOS-2 can run along-side NEMO
    with plenty of buffer space.

    The string that is returned is intended for inclusion in a bash script
    that will submitted be to the cluster queue manager via the
    :command:`sbatch` command.

    :param dict run_desc: Run description dictionary.

    :param int n_processors: Number of processors that the run will be
                             executed on.
                             For NEMO-3.6 runs this is the sum of NEMO and
                             XIOS processors.

    :param results_dir: Directory to store results into.
    :type results_dir: :py:class:`pathlib.Path`

    :param int max_tasks_per_node: Maximum number of compute tasks allowed
                                   per node. This should typically be the
                                   same as the number of processors per node;
                                   e.g. 32 on cedar/graham.computecanada.ca.

    :param str memory_per_node: Memory to request on each compute node. This
                                should typically be slightly less than the
                                total memory per node available to allow room
                                for the operating system;
                                e.g. 127G of the 128G available per node on
                                cedar/graham.computecanada.ca.

    :returns: SBATCH directives for run script.
    :rtype: Unicode str
    """
    run_id = get_run_desc_value(run_desc, ('run_id',))
    nodes = math.ceil(n_processors / max_tasks_per_node)
    try:
        td = datetime.timedelta(
            seconds=get_run_desc_value(run_desc, ('walltime',))
        )
    except TypeError:
        t = datetime.datetime.strptime(
            get_run_desc_value(run_desc, ('walltime',)), '%H:%M:%S'
        ).time()
        td = datetime.timedelta(
            hours=t.hour, minutes=t.minute, seconds=t.second
        )
    walltime = _td2hms(td)
    email = get_run_desc_value(run_desc, ('email',))
    sbatch_directives = (
        u'#SBATCH --job-name={run_id}\n'
        u'#SBATCH --nodes={nodes}\n'
        u'#SBATCH --ntasks-per-node={processors_per_node}\n'
        u'#SBATCH --mem={memory_per_node}\n'
        u'#SBATCH --time={walltime}\n'
        u'#SBATCH --mail-user={email}\n'
        u'#SBATCH --mail-type=ALL\n'
    ).format(
        run_id=run_id,
        nodes=int(nodes),
        processors_per_node=max_tasks_per_node,
        memory_per_node=memory_per_node,
        walltime=walltime,
        email=email,
    )
    try:
        account = get_run_desc_value(run_desc, ('account',), fatal=False)
        sbatch_directives += (
            u'#SBATCH --account={account}\n'.format(account=account)
        )
    except KeyError:
        logger.warning(
            'No account found in run description YAML file. '
            'If sbatch complains you can add one like account: def-allen'
        )
    sbatch_directives += (
        u'# stdout and stderr file paths/names\n'
        u'#SBATCH --output={stdout}\n'
        u'#SBATCH --error={stderr}\n'
    ).format(
        stdout=results_dir / 'stdout',
        stderr=results_dir / 'stderr',
    )
    return sbatch_directives


def _td2hms(timedelta):
    """Return a string that is the timedelta value formated as H:M:S
    with leading zeros on the minutes and seconds values.

    :param :py:obj:datetime.timedelta timedelta: Time interval to format.

    :returns: H:M:S string with leading zeros on the minutes and seconds
              values.
    :rtype: unicode
    """
    seconds = int(timedelta.total_seconds())
    periods = (('hour', 60 * 60), ('minute', 60), ('second', 1))
    hms = []
    for period_name, period_seconds in periods:
        period_value, seconds = divmod(seconds, period_seconds)
        hms.append(period_value)
    return u'{0[0]}:{0[1]:02d}:{0[2]:02d}'.format(hms)


def _definitions(
    run_desc, run_desc_file, run_dir, results_dir, queue_job_cmd, no_deflate
):
    home = '${PBS_O_HOME}' if queue_job_cmd == 'qsub' else '${HOME}'
    nemo_cmd = Path(home) / '.local/bin/nemo'
    defns = (
        u'RUN_ID="{run_id}"\n'
        u'RUN_DESC="{run_desc_file}"\n'
        u'WORK_DIR="{run_dir}"\n'
        u'RESULTS_DIR="{results_dir}"\n'
        u'COMBINE="{nemo_cmd} combine"\n'
    ).format(
        run_id=get_run_desc_value(run_desc, ('run_id',)),
        run_desc_file=run_desc_file,
        run_dir=run_dir,
        results_dir=results_dir,
        nemo_cmd=nemo_cmd,
    )
    if not no_deflate:
        defns += u'DEFLATE="{nemo_cmd} deflate"\n'.format(nemo_cmd=nemo_cmd)
    defns += u'GATHER="{nemo_cmd} gather"\n'.format(nemo_cmd=nemo_cmd)
    return defns


def _modules(modules_to_load):
    modules = u''
    for module in modules_to_load:
        modules = u''.join(
            (modules, u'module load {module}\n'.format(module=module))
        )
    return modules


def _execute(nemo_processors, xios_processors, no_deflate, max_deflate_jobs):
    mpirun = u'mpirun -np {procs} ./nemo.exe'.format(procs=nemo_processors)
    if xios_processors:
        mpirun = u' '.join(
            (mpirun, ':', '-np', str(xios_processors), './xios_server.exe')
        )
    script = (
        u'mkdir -p ${RESULTS_DIR}\n'
        u'\n'
        u'cd ${WORK_DIR}\n'
        u'echo "working dir: $(pwd)"\n'
        u'\n'
        u'echo "Starting run at $(date)"\n'
    )
    script += u'{mpirun}\n'.format(mpirun=mpirun)
    script += (
        u'MPIRUN_EXIT_CODE=$?\n'
        u'echo "Ended run at $(date)"\n'
        u'\n'
        u'echo "Results combining started at $(date)"\n'
        u'${COMBINE} ${RUN_DESC} --debug\n'
        u'echo "Results combining ended at $(date)"\n'
    )
    if not no_deflate:
        script += (
            u'\n'
            u'echo "Results deflation started at $(date)"\n'
            u'module load nco/4.6.6\n'
            u'${{DEFLATE}} *_grid_[TUVW]*.nc *_ptrc_T*.nc '
            u'--jobs {max_deflate_jobs} --debug\n'
            u'echo "Results deflation ended at $(date)"\n'
        ).format(max_deflate_jobs=max_deflate_jobs)
    script += (
        u'\n'
        u'echo "Results gathering started at $(date)"\n'
        u'${GATHER} ${RESULTS_DIR} --debug\n'
        u'echo "Results gathering ended at $(date)"\n'
    )
    return script


def _fix_permissions():
    script = (
        u'chmod go+rx ${RESULTS_DIR}\n'
        u'chmod g+rw ${RESULTS_DIR}/*\n'
        u'chmod o+r ${RESULTS_DIR}/*\n'
    )
    return script


def _cleanup():
    script = (
        u'echo "Deleting run directory" >>${RESULTS_DIR}/stdout\n'
        u'rmdir $(pwd)\n'
        u'echo "Finished at $(date)" >>${RESULTS_DIR}/stdout\n'
        u'exit ${MPIRUN_EXIT_CODE}\n'
    )
    return script
