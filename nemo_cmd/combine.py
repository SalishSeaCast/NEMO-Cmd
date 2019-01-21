# Copyright 2013-2019 The Salish Sea MEOPAR Contributors
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
"""SalishSeaCmd command plug-in for combine sub-command.

Combine per-processor files from an MPI Salish Sea NEMO run into single
files with the same name-root.
"""
import logging
import os
import shlex

try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import shutil
import subprocess

import cliff.command
import yaml

from nemo_cmd.fspath import fspath

logger = logging.getLogger(__name__)


class Combine(cliff.command.Command):
    """Combine per-processor files from an MPI NEMO run into single files
    """

    def get_parser(self, prog_name):
        parser = super(Combine, self).get_parser(prog_name)
        parser.description = """
            Combine the per-processor results and/or restart files from an MPI
            NEMO run described in DESC_FILE using the the NEMO rebuild_nemo
            tool.
            Delete the per-processor files.
        """
        parser.add_argument(
            "run_desc_file",
            type=Path,
            metavar="RUN_DESC_FILE",
            help="file path/name of run description YAML file",
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `salishsea combine` sub-command

        Run the NEMO `rebuild_nemo` tool for each set of per-processor
        results files.

        The output of `rebuild_nemo` for each file set is logged
        at the INFO level.
        """
        combine(parsed_args.run_desc_file)


def combine(run_desc_file):
    """Run the NEMO :program:`rebuild_nemo` tool for each set of
    per-processor results files.

    The output of :program:`rebuild_nemo` for each file set is logged
    at the INFO level.

    :param run_desc_file: File path/name of the run description YAML file.
    :type run_desc_file: :py:class:`pathlib.Path`
    """
    with run_desc_file.open("rt") as f:
        run_desc = yaml.safe_load(f)
    name_roots = _get_results_files()
    if name_roots:
        rebuild_nemo_script = find_rebuild_nemo_script(run_desc)
        _combine_results_files(rebuild_nemo_script, name_roots)
        _delete_results_files(name_roots)


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
    nemo_code_config = (
        Path(os.path.expandvars(run_desc["paths"]["NEMO code config"]))
        .expanduser()
        .resolve()
    )
    rebuild_nemo_exec = (
        nemo_code_config / ".." / "TOOLS" / "REBUILD_NEMO" / "rebuild_nemo.exe"
    )
    if not rebuild_nemo_exec.exists():
        logger.error(
            "{} not found - did you forget to build it?".format(rebuild_nemo_exec)
        )
        raise SystemExit(2)
    rebuild_nemo_script = rebuild_nemo_exec.with_suffix("").resolve()
    return rebuild_nemo_script


def _get_results_files():
    result_pattern = "*_0000.nc"
    name_roots = [fspath(fn.stem)[:-5] for fn in Path.cwd().glob(result_pattern)]
    if not name_roots:
        logger.info("no files found that match the {} pattern".format(result_pattern))
    return name_roots


def _combine_results_files(rebuild_nemo_script, name_roots):
    for fn in name_roots:
        files = Path.cwd().glob("{fn}_[0-9][0-9][0-9][0-9].nc".format(fn=fn))
        # Count the number of items yielded by the glob generator
        nfiles = sum(1 for _ in files)
        if nfiles == 1:
            # Results from a single processor are simply renamed
            shutil.move("{fn}_0000.nc".format(fn=fn), "{fn}.nc".format(fn=fn))
            logger.info("{fn}_0000.nc renamed to {fn}.nc".format(fn=fn))
        else:
            cmd = "{rebuild_nemo_script} {fn} {nfiles}".format(
                rebuild_nemo_script=rebuild_nemo_script, fn=fn, nfiles=nfiles
            )
            logger.info(cmd)
            result = subprocess.check_output(
                shlex.split(cmd), stderr=subprocess.STDOUT, universal_newlines=True
            )
            logger.info(result)
            os.unlink("nam_rebuild")


def _delete_results_files(name_roots):
    logger.info("Deleting per-processor files...")
    for name_root in name_roots:
        filepaths = Path.cwd().glob(
            "{name_root}_[0-9][0-9][0-9][0-9].nc".format(name_root=name_root)
        )
        for fp in filepaths:
            fp.unlink()
