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


"""NEMO command processor API

Application programming interface for the NEMO command processor.
Provides Python function interfaces to command processor sub-commands
for use in other sub-command processor modules,
and by other software.
"""
import datetime
import logging
import os
from pathlib import Path
import subprocess

import cliff.commandmanager
import yaml

from nemo_cmd import combine as combine_plugin
from nemo_cmd import deflate as deflate_plugin
from nemo_cmd import gather as gather_plugin
from nemo_cmd import prepare as prepare_plugin

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(name)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


def combine(run_desc_file):
    """Run the NEMO :program:`rebuild_nemo` tool for each set of
    per-processor results files.

    The output of :program:`rebuild_nemo` for each file set is logged
    at the INFO level.

    :param run_desc_file: File path/name of the run description YAML file.
    :type results_dir: :py:class:`pathlib.Path`
    """
    return combine_plugin.combine(run_desc_file)


def deflate(filepaths, max_concurrent_jobs):
    """Deflate variables in each of the netCDF files in filepaths using
    Lempel-Ziv compression.

    Converts files to netCDF-4 format.
    The deflated file replaces the original file.

    :param sequence filepaths: Paths/names of files to be deflated.

    :param int max_concurrent_jobs: Maximum number of concurrent deflation
                                    processes allowed.
    """
    try:
        return deflate_plugin.deflate(filepaths, max_concurrent_jobs)
    except AttributeError:
        # filepaths is sequence of path strings not Path objects
        return deflate_plugin.deflate(map(Path, filepaths), max_concurrent_jobs)


def find_rebuild_nemo_script(run_desc):
    """Calculate absolute path of the rebuild_nemo script.

    Confirm that the rebuild_nemo executable exists, raising a SystemExit
    exception if it does not.

    :param dict run_desc: Run description dictionary.

    :return: Resolved path of :file:`rebuild_nemo` script.
    :rtype: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` if the :file:`rebuild_nemo` script does not
             exist.
    """
    return combine_plugin.find_rebuild_nemo_script(run_desc)


def gather(results_dir):
    """Move all of the files and directories from the present working directory
    into results_dir.

    If results_dir doesn't exist, create it.

    Delete any symbolic links so that the present working directory is empty.

    :param results_dir: Path of the directory into which to store the run
                        results.
    :type results_dir: :py:class:`pathlib.Path`
    """
    return gather_plugin.gather(results_dir)


def prepare(run_desc_file, nocheck_init=False):
    """Prepare a NEMO run.

    A UUID named temporary run directory is created and symbolic links
    are created in the directory to the files and directories specifed
    to run NEMO.
    The output of :command:`hg parents` is recorded in the directory
    for the NEMO-code and NEMO-forcing repos that the symlinks point to.
    The path to the run directory is returned.

    :param run_desc_file: File path/name of the YAML run description file.
    :type run_desc_file: :py:class:`pathlib.Path`

    :arg nocheck_init: Suppress initial condition link check the
                       default is to check
    :type nocheck_init: boolean

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    return prepare_plugin.prepare(run_desc_file, nocheck_init)


def run_description(
    config_name="SalishSea",
    run_id=None,
    walltime=None,
    mpi_decomposition="8x18",
    NEMO_code=None,
    XIOS_code=None,
    forcing_path=None,
    runs_dir=None,
    forcing=None,
    init_conditions=None,
    namelists=None,
):
    """Return a NEMO run description dict template.

    Value may be passed for the keyword arguments to set the value of the
    corresponding items.
    Otherwise,
    the returned run description dict
    that must be updated by assignment statements to provide those values.

    .. note::

        The value of the :kbd:`['forcing']['atmospheric']` item is set to
        :file:`/results/forcing/atmospheric/GEM2.5/operational/` which is
        appropriate for runs on :kbd:`salish`, but needs to be changed for runs
        on WestGrid.

    :arg str config_name: NEMO configuration name to use for the run.

    :arg str run_id: Job identifier that appears in the :command:`qstat`
                     listing.

    :arg str walltime: Wall-clock time requested for the run.

    :arg str mpi_decomposition: MPI decomposition to use for the run.

    :arg str NEMO_code: Path to the :file:`NEMO-code/` directory where the
                        NEMO executable, etc. for the run are to be found.
                        If a relative path is used it will start from the
                        current directory.

    :arg str XIOS_code: Path to the :file:`XIOS/` directory where the
                        XIOS executable for the run are to be found.
                        If a relative path is used it will start from the
                        current directory.

    :arg str forcing_path: Path to the :file:`NEMO-forcing/` directory
                           where the netCDF files for the grid coordinates,
                           bathymetry, initial conditions, open boundary
                           conditions, etc. are found.
                           If a relative path is used it will start from
                           the current directory.

    :arg str runs_dir: Path to the directory where run directories will be
                       created.
                       If a relative path is used it will start from the
                       current directory.

    :arg dict forcing: Forcing link data structure.
                       The default of :py:obj:`None` produces "sensible
                       defaults" for NEMO-3.4,
                       but :py:obj:`None` for NEMO-3.6.
                       See the :ref:`RunDescriptionFileStructure` docs
                       for the version of NEMO that you are using for
                       details of the data structure.

    :arg str init_conditions: Name of sub-directory in :file:`NEMO-forcing/`
                              where initial conditions files are to be found,
                              or the path to and name of a restart file.
                              If a relative path is used for a restart file
                              it will start from the  current directory.

    :arg dict namelists: Namelists data structure.
                         The default of :py:obj:`None` produces "sensible
                         defaults" for a physics-only run for both NEMO-3.4,
                         annd NEMO-3.6.
                         See the :ref:`RunDescriptionFileStructure` docs
                         for the version of NEMO that you are using for
                         details of the data structure.

    """
    run_description = {
        "config_name": config_name,
        "MPI decomposition": mpi_decomposition,
        "run_id": run_id,
        "walltime": walltime,
        "paths": {
            "NEMO-code": NEMO_code,
            "XIOS": XIOS_code,
            "forcing": forcing_path,
            "runs directory": runs_dir,
        },
        "grid": {
            "coordinates": "coordinates_seagrid_SalishSea.nc",
            "bathymetry": "bathy_meter_SalishSea2.nc",
        },
        "forcing": forcing,
        "output": {"files": "iodef.xml"},
    }
    if namelists is None:
        run_description["namelists"] = {
            "namelist_cfg": [
                "namelist.time",
                "namelist.domain",
                "namelist.surface",
                "namelist.lateral",
                "namelist.bottom",
                "namelist.tracer",
                "namelist.dynamics",
                "namelist.vertical",
                "namelist.compute",
            ]
        }
    else:
        run_description["namelists"] = namelists
    run_description["output"].update(
        {
            "domain": "domain_def.xml",
            "fields": None,
            "separate XIOS server": True,
            "XIOS servers": 1,
        }
    )
    if NEMO_code is not None:
        run_description["output"]["fields"] = os.path.join(
            NEMO_code, "NEMOGCM/CONFIG/SHARED/field_def.xml"
        )
    return run_description


def run_in_subprocess(run_id, run_desc, results_dir):
    """Execute `nemo run` in a subprocess.

    :arg str run_id: Job identifier that appears in the :command:`qstat`
                     listing.
                     A temporary run description YAML file is created
                     with the name :file:`{run_id}_subprocess_run.yaml`.

    :arg dict run_desc: Run description data structure that will be
                        written to the temporary YAML file.

    :arg results_dir: Directory to store results into.
    :type results_dir: str
    """
    yaml_file = f"{run_id}_subprocess_run.yaml"
    with open(yaml_file, "wt") as f:
        yaml.dump(run_desc, f, default_flow_style=False)
    cmd = ["salishsea", "run"]
    cmd.extend([yaml_file, results_dir])
    try:
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, universal_newlines=True
        )
        for line in output.splitlines():
            if line:
                log.info(line)
    except subprocess.CalledProcessError as e:
        log.error(f"subprocess {cmd} failed with return code {e.returncode}")
        for line in e.output.splitlines():
            if line:
                log.error(line)
    os.unlink(yaml_file)


def _run_subcommand(app, app_args, argv):
    """Run a sub-command with argv as arguments via its plug-in
    interface.

    Based on :py:meth:`cliff.app.run_subcommand`.

    :arg app: Application instance invoking the command.
    :type app: :py:class:`cliff.app.App`

    :arg app_args: Application arguments.
    :type app_args: :py:class:`argparse.Namespace`

    :arg argv: Sub-command arguments.
    :type argv: list
    """
    command_manager = cliff.commandmanager.CommandManager(
        "salishsea.app", convert_underscores=False
    )
    try:
        subcommand = command_manager.find_command(argv)
    except ValueError as err:
        if app_args.debug:
            raise
        else:
            log.error(err)
        return 2
    cmd_factory, cmd_name, sub_argv = subcommand
    cmd = cmd_factory(app, app_args)
    try:
        cmd_parser = cmd.get_parser(cmd_name)
        parsed_args = cmd_parser.parse_args(sub_argv)
        result = cmd.take_action(parsed_args)
    except Exception as err:
        result = 1
        if app_args.debug:
            log.exception(err)
        else:
            log.error(err)
    return result


def pbs_common(run_description, n_processors, email, results_dir, pmem="2000mb"):
    """Return the common PBS directives used to run NEMO in a TORQUE/PBS
    multiple processor context.

    The string that is returned is intended for inclusion in a bash script
    that will be to the TORQUE/PBS queue manager via the :command:`qsub`
    command.

    :arg dict run_description: Run description data structure.

    :arg int n_processors: Number of processors that the run will be
                           executed on.
                           For NEMO-3.6 runs this is the sum of NMEO and
                           XIOS processors.

    :arg str email: Email address to send job begin, end & abort
                    notifications to.

    :arg results_dir: Directory to store results into.
    :type results_dir: str or :py:class:`pathlib.Path`

    :arg str pmem: Memory per processor.

    :returns: PBS directives for run script.
    :rtype: Unicode str
    """
    try:
        td = datetime.timedelta(seconds=run_description["walltime"])
    except TypeError:
        t = datetime.datetime.strptime(run_description["walltime"], "%H:%M:%S").time()
        td = datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
    walltime = td2hms(td)
    pbs_directives = (
        f"#PBS -N {run_description['run_id']}\n"
        f"#PBS -S /bin/bash\n"
        f"#PBS -l procs={n_processors}\n"
        f"# memory per processor\n"
        f"#PBS -l pmem={pmem}\n"
        f"#PBS -l walltime={walltime}\n"
        f"# email when the job [b]egins and [e]nds, or is [a]borted\n"
        f"#PBS -m bea\n"
        f"#PBS -M {email}\n"
        f"# stdout and stderr file paths/names\n"
        f"#PBS -o {results_dir}/stdout\n"
        f"#PBS -e {results_dir}/stderr\n"
    )
    return pbs_directives


def td2hms(timedelta):
    """Return a string that is the timedelta value formated as H:M:S
    with leading zeros on the minutes and seconds values.

    :arg timedelta: Time interval to format.
    :type timedelta: :py:obj:datetime.timedelta

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
