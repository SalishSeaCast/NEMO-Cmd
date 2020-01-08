# Copyright 2013-2020 The Salish Sea MEOPAR Contributors
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
"""NEMO-Cmd command plug-in for gather sub-command.

Gather results files from a NEMO run into a specified directory.
"""
import logging
import shutil
from pathlib import Path

import cliff.command

from nemo_cmd.fspath import fspath

logger = logging.getLogger(__name__)


class Gather(cliff.command.Command):
    """Gather results from a NEMO run.
    """

    def get_parser(self, prog_name):
        parser = super(Gather, self).get_parser(prog_name)
        parser.description = """
            Gather the results files from the NEMO run in the present working
            directory into files in RESULTS_DIR.
            The run description file,
            namelist(s),
            and other files that define the run are also gathered into
            RESULTS_DIR.

            If RESULTS_DIR does not exist it will be created.
        """
        parser.add_argument(
            "results_dir",
            type=Path,
            metavar="RESULTS_DIR",
            help="directory to store results into",
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `nemo gather` sub-command.

        Gather the results files from a NEMO run into a results directory.

        The run description file,
        namelist(s),
        and other files that define the run are also gathered into the
        directory given by `parsed_args.results_dir`.
        """
        gather(parsed_args.results_dir)


def gather(results_dir):
    """Move all of the files and directories from the present working directory
    into results_dir.

    If results_dir doesn't exist, create it.

    Delete any symbolic links so that the present working directory is empty.

    :param results_dir: Path of the directory into which to store the run
                        results.
    :type results_dir: :py:class:`pathlib.Path`
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    symlinks = {p for p in Path.cwd().glob("*") if p.is_symlink()}
    try:
        _move_results(results_dir, symlinks)
    except Exception:
        raise
    _delete_symlinks(symlinks)


def _move_results(results_dir, symlinks):
    cwd = Path.cwd()
    abs_results_dir = results_dir.resolve()
    if cwd.samefile(abs_results_dir):
        return
    logger.info("Moving run definition and results files...")
    for p in cwd.glob("*"):
        if p not in symlinks:
            src = p.relative_to(cwd)
            suffix = "/" if src.is_dir() else ""
            logger.info("Moving {}{} to {}/".format(src, suffix, abs_results_dir))
            if src.is_dir():
                shutil.move(fspath(src), fspath(abs_results_dir))
            else:
                shutil.move(fspath(src), fspath(abs_results_dir / src))


def _delete_symlinks(symlinks):
    logger.info("Deleting symbolic links...")
    for ln in symlinks:
        ln.unlink()
