# Copyright 2013-2017 The Salish Sea MEOPAR Contributors
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

import logging
import math
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
from nemo_cmd.prepare import get_run_desc_value

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
            '--nemo3.4',
            dest='nemo34',
            action='store_true',
            help='''
            Do a NEMO-3.4 run;
            the default is to do a NEMO-3.6 run'''
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
            parsed_args.nemo34,
            parsed_args.nocheck_init,
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
    nemo34=False,
    nocheck_init=False,
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

    :param boolean nemo34: Prepare a NEMO-3.4 run;
                           the default is to prepare a NEMO-3.6 run

    :param boolean nocheck_init: Suppress initial condition link check
                                 the default is to check

    :param boolean no_submit: Prepare the temporary run directory,
                              and the bash script to execute the NEMO run,
                              but don't submit the run to the queue.

    :param int waitjob: Use -W waitjob in call to qsub, to make current job
                        wait for on waitjob.  Waitjob is the queue job number

    :param str queue_job_cmd: Command to use to submit the bash script to execute the NEMO run.

    :param boolean quiet: Don't show the run directory path message;
                          the default is to show the temporary run directory
                          path.

    :returns: Message generated by queue manager upon submission of the
              run script.
    :rtype: str
    """
    run_dir = api.prepare(desc_file, nemo34, nocheck_init)
    if not quiet:
        logger.info('Created run directory {}'.format(run_dir))
    run_desc = lib.load_run_desc(desc_file)
    nemo_processors = lib.get_n_processors(run_desc)
    separate_xios_server = get_run_desc_value(
        run_desc, ('output', 'separate XIOS server')
    )
    if not nemo34 and separate_xios_server:
        xios_processors = get_run_desc_value(
            run_desc, ('output', 'XIOS servers')
        )
    else:
        xios_processors = 0
    results_dir = Path(results_dir)
    batch_script = _build_batch_script(
        run_desc,
        fspath(desc_file), nemo_processors, xios_processors, max_deflate_jobs,
        results_dir, run_dir
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
    qsub_msg = subprocess.check_output(cmd.split(), universal_newlines=True)
    os.chdir(fspath(starting_dir))
    return qsub_msg


def _build_batch_script(
    run_desc, desc_file, nemo_processors, xios_processors, max_deflate_jobs,
    results_dir, run_dir
):
    """Build the Bash script that will execute the run.

    :param dict run_desc: Run description dictionary.

    :param str desc_file: File path/name of the YAML run description file.

    :param int nemo_processors: Number of processors that NEMO will be executed
                                on.

    :param int xios_processors: Number of processors that XIOS will be executed
                                on.

    :param int max_deflate_jobs: Maximum number of concurrent sub-processes to
                                 use for netCDF deflating.

    :param results_dir: Path of the directory in which to store the run
                        results;
                        it will be created if it does not exist.
    :type results_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Bash script to execute the run.
    :rtype: str
    """
    script = u'#!/bin/bash\n'
    email = get_run_desc_value(run_desc, ('email',))
    script = u'\n'.join((
        script, u'{pbs_common}\n'.format(
            pbs_common=api.pbs_common(
                run_desc, nemo_processors + xios_processors, email, results_dir
            )
        )
    ))
    if 'PBS resources' in run_desc:
        script = u''.join((
            script[:-1],
            '# resource(s) requested in run description YAML file\n'
        ))
        script = u''.join((
            script, u'{pbs_resources}\n'.format(
                pbs_resources=_pbs_resources(
                    run_desc['PBS resources'],
                    nemo_processors + xios_processors
                )
            )
        ))
    script = u'\n'.join((
        script, u'{defns}\n'.format(
            defns=_definitions(run_desc, desc_file, run_dir, results_dir),
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
                nemo_processors, xios_processors, max_deflate_jobs
            ),
            fix_permissions=_fix_permissions(),
            cleanup=_cleanup(),
        )
    ))
    return script


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


def _definitions(run_desc, run_desc_file, run_dir, results_dir):
    defns = (
        u'RUN_ID="{run_id}"\n'
        u'RUN_DESC="{run_desc_file}"\n'
        u'WORK_DIR="{run_dir}"\n'
        u'RESULTS_DIR="{results_dir}"\n'
        u'COMBINE="{nemo_cmd} combine"\n'
        u'DEFLATE="{nemo_cmd} deflate"\n'
        u'GATHER="{nemo_cmd} gather"\n'
    ).format(
        run_id=get_run_desc_value(run_desc, ('run_id',)),
        run_desc_file=run_desc_file,
        run_dir=run_dir,
        results_dir=results_dir,
        nemo_cmd=Path('${PBS_O_HOME}/.local/bin/nemo'),
    )
    return defns


def _modules(modules_to_load):
    modules = u''
    for module in modules_to_load:
        modules = u''.join(
            (modules, u'module load {module}\n'.format(module=module))
        )
    return modules


def _execute(nemo_processors, xios_processors, max_deflate_jobs):
    mpirun = u'mpirun -np {procs} ./nemo.exe'.format(procs=nemo_processors)
    if xios_processors:
        mpirun = u' '.join(
            (mpirun, ':', '-np', str(xios_processors), './xios_server.exe')
        )
    script = (
        u'cd ${WORK_DIR}\n'
        u'echo "working dir: $(pwd)"\n'
        u'\n'
        u'echo "Starting run at $(date)"\n'
        u'mkdir -p ${RESULTS_DIR}\n'
    )
    script += u'{mpirun}\n'.format(mpirun=mpirun)
    script += (
        u'MPIRUN_EXIT_CODE=$?\n'
        u'echo "Ended run at $(date)"\n'
        u'\n'
        u'echo "Results combining started at $(date)"\n'
        u'${{COMBINE}} ${{RUN_DESC}} --debug\n'
        u'echo "Results combining ended at $(date)"\n'
        u'\n'
        u'echo "Results deflation started at $(date)"\n'
        u'${{DEFLATE}} *_grid_[TUVW]*.nc *_ptrc_T*.nc '
        u'--jobs {max_deflate_jobs} --debug\n'
        u'echo "Results deflation ended at $(date)"\n'
        u'\n'
        u'echo "Results gathering started at $(date)"\n'
        u'${{GATHER}} ${{RESULTS_DIR}} --debug\n'
        u'echo "Results gathering ended at $(date)"\n'
    ).format(max_deflate_jobs=max_deflate_jobs)
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
