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


"""NEMO-Cmd command plug-in for deflate sub-command.

Deflate variables in netCDF files using Lempel-Ziv compression.
"""
import logging
import math
import multiprocessing
from pathlib import Path
import shlex
import subprocess
import time

import attr
import cliff.command

logger = logging.getLogger(__name__)


class Deflate(cliff.command.Command):
    """Deflate variables in netCDF files using Lempel-Ziv compression."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.description = """
            Deflate variables in netCDF files using Lempel-Ziv compression.
            Converts files to netCDF-4 format.
            The deflated file replaces the original file.
            This command is effectively the same as running
            ncks -4 -L -O FILEPATH FILEPATH
            for each FILEPATH.
        """
        parser.add_argument(
            "filepaths",
            nargs="+",
            type=Path,
            metavar="FILEPATH",
            help="Path/name of file to be deflated.",
        )
        parser.add_argument(
            "-j",
            "--jobs",
            type=int,
            default=math.floor(multiprocessing.cpu_count() / 2),
            help=(
                "Maximum number of concurrent deflation processes allowed. "
                "Defaults to 1/2 the number of cores detected."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the :command:`nemo deflate` sub-command.

        Deflate variables in netCDF files using Lempel-Ziv compression.
        Converts files to netCDF-4 format.
        The deflated file replaces the original file.
        This command is effectively the same as
        :command:`ncks -4 -L -O filename filename`.
        """
        deflate(parsed_args.filepaths, parsed_args.jobs)


@attr.s
class DeflateJob(object):
    """netCDF file deflation job."""

    #: Path/name of the netCDF file to deflate.
    filepath = attr.ib()
    #: Lempel-Ziv compression level to use.
    dfl_lvl = attr.ib(default=4)
    #: Deflation job subprocess object.
    process = attr.ib(default=None)
    #: Deflation job process PID.
    pid = attr.ib(default=None)
    #: Deflation job process return code.
    returncode = attr.ib(default=None)

    def start(self):
        """Start the deflation job in a subprocess.

        Cache the subprocess object and its process id as job attributes.
        """
        cmd = (
            f"nccopy -s -4 -d{self.dfl_lvl} {self.filepath} {self.filepath}.nccopy.tmp"
        )
        self.process = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        self.pid = self.process.pid
        logger.debug(f"deflating {self.filepath} in process {self.pid}")

    @property
    def done(self):
        """Return a boolean indicating whether the job has finished.

        Cache the subprocess return code as a job attribute.
        """
        finished = False
        self.returncode = self.process.poll()
        if self.returncode is not None:
            if self.returncode == 0:
                Path(f"{self.filepath}.nccopy.tmp").rename(self.filepath)
            finished = True
            logger.debug(
                f"deflating {self.filepath} finished with return code {self.returncode}"
            )
        return finished


def deflate(filepaths, max_concurrent_jobs):
    """Deflate variables in each of the netCDF files in filepaths using
    Lempel-Ziv compression.

    Converts file to netCDF-4 format.
    The deflated file replaces the original file.

    :param sequence filepaths: Paths/names of files to be deflated.

    :param int max_concurrent_jobs: Maximum number of concurrent deflation
    processes allowed.
    """
    logger.info(
        f"Deflating in up to {int(max_concurrent_jobs)} concurrent sub-processes"
    )
    jobs = [DeflateJob(fp) for fp in filepaths if fp.exists()]
    jobs_in_progress = _launch_initial_jobs(jobs, max_concurrent_jobs)
    while jobs or jobs_in_progress:
        time.sleep(1)
        _poll_and_launch(jobs, jobs_in_progress)


def _launch_initial_jobs(jobs, max_concurrent_jobs):
    jobs_in_progress = {}
    for process in range(int(max_concurrent_jobs)):
        try:
            job = jobs.pop(0)
        except IndexError:
            break
        else:
            job.start()
            jobs_in_progress[job.pid] = job
    return jobs_in_progress


def _poll_and_launch(jobs, jobs_in_progress):
    for running_job in jobs_in_progress.copy().values():
        if running_job.done:
            result, _ = running_job.process.communicate()
            (
                logger.error(result)
                if result
                else logger.info(f"netCDF4 deflated {running_job.filepath}")
            )
            jobs_in_progress.pop(running_job.pid)
            try:
                job = jobs.pop(0)
            except IndexError:
                continue
            else:
                job.start()
                jobs_in_progress[job.pid] = job
