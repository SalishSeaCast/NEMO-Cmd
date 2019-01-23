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
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, Mock, patch

import cliff.app
import pytest

import nemo_cmd.deflate


@pytest.fixture
def deflate_cmd():
    return nemo_cmd.deflate.Deflate(Mock(spec=cliff.app.App), [])


class TestParser:
    """Unit tests for `nemo deflate` sub-command command-line parser.
    """

    def test_get_parser(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        assert parser.prog == "nemo deflate"

    def test_parsed_args(self, deflate_cmd):
        parser = deflate_cmd.get_parser("nemo deflate")
        parsed_args = parser.parse_args(["foo.nc", "bar.nc", "-j6"])
        assert parsed_args.filepaths == [Path("foo.nc"), Path("bar.nc")]
        assert parsed_args.jobs == 6


class TestTakeAction:
    """Unit test for `nemo deflate` sub-command take_action() method.
    """

    @patch("nemo_cmd.deflate.deflate", autospec=True)
    def test_take_action(self, m_deflate, deflate_cmd):
        parsed_args = SimpleNamespace(
            filepaths=[Path("foo.nc"), Path("bar.nc")], jobs=6
        )
        deflate_cmd.take_action(parsed_args)
        m_deflate.assert_called_once_with([Path("foo.nc"), Path("bar.nc")], 6)
