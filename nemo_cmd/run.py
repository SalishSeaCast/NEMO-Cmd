# Copyright 2013 – present by the SalishSeaCast contributors
# and The University of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# SPDX-License-Identifier: Apache-2.0


"""NEMO-Cmd command plug-in for run sub-command.

Prepare for, execute, and gather the results of a run of the NEMO model.
"""
import datetime
import logging
import math
import shlex
import time
import os
from pathlib import Path
import subprocess

import cliff.command

from nemo_cmd import api
from nemo_cmd.fspath import fspath
from nemo_cmd.prepare import get_n_processors, get_run_desc_value, load_run_desc

logger = logging.getLogger(__name__)


class Run(cliff.command.Command):
    """Prepare, execute, and gather results from a NEMO model run."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.description = """
            Prepare, execute, and gather the results from a NEMO
            run described in DESC_FILE.
            The results files from the run are gathered in RESULTS_DIR.

            If RESULTS_DIR does not exist it will be created.
        """
        parser.add_argument(
            "desc_file",
            metavar="DESC_FILE",
            type=Path,
            help="run description YAML file",
        )
        parser.add_argument(
            "results_dir", metavar="RESULTS_DIR", help="directory to store results into"
        )
        parser.add_argument(
            "--max-deflate-jobs",
            dest="max_deflate_jobs",
            type=int,
            default=4,
            help="""
            Maximum number of concurrent sub-processes to
            use for netCDF deflating. Defaults to 4.""",
        )
        parser.add_argument(
            "--nocheck-initial-conditions",
            dest="nocheck_init",
            action="store_true",
            help="""
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to wait on a
            previous job""",
        )
        parser.add_argument(
            "--no-deflate",
            dest="no_deflate",
            action="store_true",
            help="""
            Do not include "nemo deflate" command in the bash script.
            Use this option if you are using on-the-fly deflation in XIOS-2;
            i.e. you are using 1 XIOS-2 process and have the
            compression_level="4" attribute set in all of the file_group
            definitions in your file_def.xml file.
            """,
        )
        parser.add_argument(
            "--no-submit",
            dest="no_submit",
            action="store_true",
            help="""
            Prepare the temporary run directory, and the bash script to execute
            the NEMO run, but don't submit the run to the queue.
            This is useful during development runs when you want to hack on the
            bash script and/or use the same temporary run directory more than
            once.
            """,
        )
        parser.add_argument(
            "--waitjob",
            type=int,
            default=0,
            help="""
            use -W waitjob in call to qsub, to make current job
            wait for on waitjob.  Waitjob is the queue job number
            """,
        )
        parser.add_argument(
            "--queue-job-cmd",
            dest="queue_job_cmd",
            type=str,
            choices={"qsub", "sbatch"},
            default="qsub",
            help="""
            Command to use to submit the bash script to execute the NEMO run;
            defaults to qsub.
            """,
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="don't show the run directory path or job submission message",
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
            quiet=parsed_args.quiet,
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
    queue_job_cmd="qsub",
    quiet=False,
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
        logger.info(f"Created run directory {run_dir}")
    run_desc = load_run_desc(desc_file)
    nemo_processors = get_n_processors(run_desc, run_dir)
    separate_xios_server = get_run_desc_value(
        run_desc, ("output", "separate XIOS server")
    )
    xios_processors = (
        get_run_desc_value(run_desc, ("output", "XIOS servers"))
        if separate_xios_server
        else 0
    )
    results_dir = Path(results_dir)
    batch_script = _build_batch_script(
        run_desc,
        fspath(desc_file),
        nemo_processors,
        xios_processors,
        no_deflate,
        max_deflate_jobs,
        results_dir,
        run_dir,
        queue_job_cmd,
    )
    batch_file = run_dir / "NEMO.sh"
    with batch_file.open("wt") as f:
        f.write(batch_script)
    if no_submit:
        return
    starting_dir = Path.cwd()
    os.chdir(fspath(run_dir))
    if waitjob:
        depend_opt = "-W depend=afterok" if queue_job_cmd == "qsub" else "-d afterok"
        cmd = f"{queue_job_cmd} {depend_opt}:{waitjob} NEMO.sh"
    else:
        cmd = f"{queue_job_cmd} NEMO.sh"
    results_dir.mkdir(parents=True, exist_ok=True)
    try:
        submit_job_msg = subprocess.check_output(
            shlex.split(cmd), universal_newlines=True
        )
    except OSError:
        logger.error(
            f"{queue_job_cmd} not found. Please confirm the correct job submission command "
            f"(qsub or sbatch) for this platform and use the --job-queue-cmd command-line option."
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
    run_desc,
    desc_file,
    nemo_processors,
    xios_processors,
    no_deflate,
    max_deflate_jobs,
    results_dir,
    run_dir,
    queue_job_cmd,
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
    script = "#!/bin/bash\n"
    scheduler_directives = {"qsub": _pbs_directives, "sbatch": _sbatch_directives}
    script = "\n".join(
        (
            script,
            scheduler_directives[queue_job_cmd](
                run_desc, nemo_processors + xios_processors, results_dir
            ),
        )
    )
    script = (
        f"{script}\n"
        f"{_definitions(run_desc, desc_file, run_dir, results_dir, queue_job_cmd, no_deflate)}\n"
    )
    if "modules to load" in run_desc:
        script = f"{script}\n" f"{_modules(run_desc['modules to load'])}\n"
    script = (
        f"{script}\n"
        f"{_execute(nemo_processors, xios_processors, no_deflate, max_deflate_jobs)}\n"
        f"{_fix_permissions()}\n"
        f"{_cleanup()}"
    )
    return script


def _pbs_directives(run_desc, n_processors, results_dir):
    email = get_run_desc_value(run_desc, ("email",))
    pbs_directives = "".join(
        (f"{api.pbs_common(run_desc, n_processors, email, results_dir)}\n")
    )
    if "PBS resources" in run_desc:
        pbs_directives = "".join(
            (
                pbs_directives[:-1],
                "# resource(s) requested in run description YAML file\n",
            )
        )
        pbs_directives = "".join(
            (
                pbs_directives,
                f"{_pbs_resources(run_desc['PBS resources'], n_processors)}\n",
            )
        )
    return pbs_directives


def _pbs_resources(resources, n_processors):
    pbs_directives = ""
    for resource in resources:
        if "nodes=" in resource and ":ppn=" in resource:
            _, ppn = resource.rsplit("=", 1)
            nodes = math.ceil(n_processors / int(ppn))
            resource = f"nodes={int(nodes)}:ppn={ppn}"
        pbs_directives = "".join((pbs_directives, f"#PBS -l {resource}\n"))
    return pbs_directives


def _sbatch_directives(
    run_desc, n_processors, results_dir, max_tasks_per_node=32, memory_per_node=0
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
    run_id = get_run_desc_value(run_desc, ("run_id",))
    nodes = math.ceil(n_processors / max_tasks_per_node)
    try:
        td = datetime.timedelta(seconds=get_run_desc_value(run_desc, ("walltime",)))
    except TypeError:
        t = datetime.datetime.strptime(
            get_run_desc_value(run_desc, ("walltime",)), "%H:%M:%S"
        ).time()
        td = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    walltime = _td2hms(td)
    email = get_run_desc_value(run_desc, ("email",))
    sbatch_directives = (
        f"#SBATCH --job-name={run_id}\n"
        f"#SBATCH --nodes={nodes}\n"
        f"#SBATCH --ntasks-per-node={max_tasks_per_node}\n"
        f"#SBATCH --mem={memory_per_node}\n"
        f"#SBATCH --time={walltime}\n"
        f"#SBATCH --mail-user={email}\n"
        f"#SBATCH --mail-type=ALL\n"
    )
    try:
        account = get_run_desc_value(run_desc, ("account",), fatal=False)
        sbatch_directives += f"#SBATCH --account={account}\n"
    except KeyError:
        logger.warning(
            "No account found in run description YAML file. "
            "If sbatch complains you can add one like account: def-allen"
        )
    sbatch_directives += (
        f"# stdout and stderr file paths/names\n"
        f"#SBATCH --output={results_dir / 'stdout'}\n"
        f"#SBATCH --error={results_dir / 'stderr'}\n"
    )
    return sbatch_directives


def _td2hms(timedelta):
    """Return a string that is the timedelta value formated as H:M:S
    with leading zeros on the minutes and seconds values.

    :param :py:obj:`datetime.timedelta` timedelta: Time interval to format.

    :returns: H:M:S string with leading zeros on the minutes and seconds
              values.
    :rtype: str
    """
    seconds = int(timedelta.total_seconds())
    periods = (("hour", 60 * 60), ("minute", 60), ("second", 1))
    hms = []
    for period_name, period_seconds in periods:
        period_value, seconds = divmod(seconds, period_seconds)
        hms.append(period_value)
    return f"{hms[0]}:{hms[1]:02d}:{hms[2]:02d}"


def _definitions(
    run_desc, run_desc_file, run_dir, results_dir, queue_job_cmd, no_deflate
):
    home = "${PBS_O_HOME}" if queue_job_cmd == "qsub" else "${HOME}"
    nemo_cmd = Path(home) / ".local/bin/nemo"
    defns = (
        f'RUN_ID="{get_run_desc_value(run_desc, ("run_id",))}"\n'
        f'RUN_DESC="{run_desc_file}"\n'
        f'WORK_DIR="{run_dir}"\n'
        f'RESULTS_DIR="{results_dir}"\n'
        f'COMBINE="{nemo_cmd} combine"\n'
    )
    if not no_deflate:
        defns += f'DEFLATE="{nemo_cmd} deflate"\n'
    defns += f'GATHER="{nemo_cmd} gather"\n'
    return defns


def _modules(modules_to_load):
    modules = ""
    for module in modules_to_load:
        modules = "".join((modules, f"module load {module}\n"))
    return modules


def _execute(nemo_processors, xios_processors, no_deflate, max_deflate_jobs):
    mpirun = f"mpirun -np {nemo_processors} ./nemo.exe"
    if xios_processors:
        mpirun = " ".join(
            (mpirun, ":", "-np", str(xios_processors), "./xios_server.exe")
        )
    script = (
        "mkdir -p ${RESULTS_DIR}\n"
        "\n"
        "cd ${WORK_DIR}\n"
        'echo "working dir: $(pwd)"\n'
        "\n"
        'echo "Starting run at $(date)"\n'
    )
    script += f"{mpirun}\n"
    script += (
        "MPIRUN_EXIT_CODE=$?\n"
        'echo "Ended run at $(date)"\n'
        "\n"
        'echo "Results combining started at $(date)"\n'
        "${COMBINE} ${RUN_DESC} --debug\n"
        'echo "Results combining ended at $(date)"\n'
    )
    if not no_deflate:
        script += (
            f"\n"
            f'echo "Results deflation started at $(date)"\n'
            f"module load nco/4.6.6\n"
            f"${{DEFLATE}} *_grid_[TUVW]*.nc *_ptrc_T*.nc "
            f"--jobs {max_deflate_jobs} --debug\n"
            f'echo "Results deflation ended at $(date)"\n'
        )
    script += (
        "\n"
        'echo "Results gathering started at $(date)"\n'
        "${GATHER} ${RESULTS_DIR} --debug\n"
        'echo "Results gathering ended at $(date)"\n'
    )
    return script


def _fix_permissions():
    script = (
        "chmod go+rx ${RESULTS_DIR}\n"
        "chmod g+rw ${RESULTS_DIR}/*\n"
        "chmod o+r ${RESULTS_DIR}/*\n"
    )
    return script


def _cleanup():
    script = (
        'echo "Deleting run directory" >>${RESULTS_DIR}/stdout\n'
        "rmdir $(pwd)\n"
        'echo "Finished at $(date)" >>${RESULTS_DIR}/stdout\n'
        "exit ${MPIRUN_EXIT_CODE}\n"
    )
    return script
