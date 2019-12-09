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
"""NEMO-Cmd deflate sub-command plug-in unit tests
"""
import logging
import math
import multiprocessing
from pathlib import Path
from types import SimpleNamespace

import pytest

import nemo_cmd.main
import nemo_cmd.deflate


@pytest.fixture
def deflate_cmd():
    return nemo_cmd.deflate.Deflate(nemo_cmd.main.NEMO_App, [])


class TestParser:
    """Unit tests for `nemo deflate` sub-command command-line parser.
    """

    def test_get_parser(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        assert parser.prog == "nemo deflate"

    def test_cmd_description(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        assert parser.description.strip().startswith(
            "Deflate variables in netCDF files using Lempel-Ziv compression."
        )

    def test_filepaths_argument(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        assert parser._actions[1].dest == "filepaths"
        assert parser._actions[1].metavar == "FILEPATH"
        assert parser._actions[1].type == Path
        assert parser._actions[1].help

    def test_jobs_option(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        assert parser._actions[2].dest == "jobs"
        assert parser._actions[2].type == int
        assert parser._actions[2].default == math.floor(multiprocessing.cpu_count() / 2)
        assert parser._actions[2].help

    def test_parsed_arg(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        parsed_args = parser.parse_args(["foo.nc", "bar.nc"])
        assert parsed_args.filepaths == [Path("foo.nc"), Path("bar.nc")]

    def test_parsed_args_option_default(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        parsed_args = parser.parse_args(["foo.nc"])
        assert parsed_args.jobs == math.floor(multiprocessing.cpu_count() / 2)

    def test_parsed_args_option_value(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        parsed_args = parser.parse_args(["foo.nc", "-j6"])
        assert parsed_args.jobs == 6


class TestTakeAction:
    """Unit test for `nemo deflate` sub-command take_action() method.
    """

    def test_take_action(self, deflate_cmd, caplog, monkeypatch):

        parsed_args = SimpleNamespace(
            filepaths=[Path("foo.nc"), Path("bar.nc")], jobs=6
        )
        caplog.set_level(logging.INFO)
        deflate_cmd.take_action(parsed_args)
        assert caplog.records[0].levelname == "INFO"
        expected = "Deflating in up to 6 concurrent sub-processes"
        assert caplog.messages[0] == expected
