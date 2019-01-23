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
"""NEMO-Cmd gather sub-command plug-in unit tests
"""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import cliff.app
import pytest

import nemo_cmd.gather


@pytest.fixture
def gather_cmd():
    return nemo_cmd.gather.Gather(Mock(spec=cliff.app.App), [])


class TestGetParser:
    """Unit tests for `nemo gather` sub-command command-line parser.
    """

    def test_get_parser(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        assert parser.prog == "nemo gather"

    def test_parsed_args_defaults(self, gather_cmd):
        parser = gather_cmd.get_parser("nemo gather")
        parsed_args = parser.parse_args(["/results/"])
        assert parsed_args.results_dir == Path("/results/")


class TestTakeAction:
    """Unit test for `nemo gather` sub-command take_action() method.
    """

    @patch("nemo_cmd.gather.gather", autospec=True)
    def test_take_action(self, m_gather, gather_cmd):
        parsed_args = SimpleNamespace(results_dir=Path("/results/"))
        gather_cmd.take_action(parsed_args)
        m_gather.assert_called_once_with(Path("/results/"))
