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
"""NEMO-Cmd gather sub-command plug-in unit tests
"""
from pathlib import Path
from types import SimpleNamespace

import pytest

import nemo_cmd.main
import nemo_cmd.gather


@pytest.fixture
def gather_cmd():
    return nemo_cmd.gather.Gather(nemo_cmd.main.NEMO_App, [])


class TestGetParser:
    """Unit tests for `nemo gather` sub-command command-line parser.
    """

    def test_get_parser(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        assert parser.prog == "nemo gather"

    def test_cmd_description(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        assert parser.description.strip().startswith(
            "Gather the results files from the NEMO run in the present working"
        )

    def test_results_dir_argument(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        assert parser._actions[1].dest == "results_dir"
        assert parser._actions[1].metavar == "RESULTS_DIR"
        assert parser._actions[1].type == Path
        assert parser._actions[1].help

    def test_parsed_args_defaults(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        parsed_args = parser.parse_args(["/results/"])
        assert parsed_args.results_dir == Path("/results/")


class TestTakeAction:
    """Unit test for `nemo gather` sub-command take_action() method.
    """

    def test_take_action(self, gather_cmd, tmp_path, monkeypatch):
        def mock_move_results(*args):
            pass

        def mock_delete_symlinks(*args):
            pass

        monkeypatch.setattr(nemo_cmd.gather, "_move_results", mock_move_results)
        monkeypatch.setattr(nemo_cmd.gather, "_delete_symlinks", mock_delete_symlinks)
        results_dir = tmp_path / "results_dir"
        parsed_args = SimpleNamespace(results_dir=results_dir)
        gather_cmd.take_action(parsed_args)
        assert results_dir.exists()
