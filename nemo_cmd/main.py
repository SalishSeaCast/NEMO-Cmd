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


"""NEMO_Cmd application

NEMO Command Processor

This module is connected to the :command:`nemo` command via a scripts and
entry-points configuration in :file:`pyproject.toml`.
"""
import importlib.metadata
import sys

import cliff.app
import cliff.commandmanager

import nemo_cmd


class NEMO_App(cliff.app.App):
    CONSOLE_MESSAGE_FORMAT = "%(name)s %(levelname)s: %(message)s"

    def __init__(self):
        super().__init__(
            description="NEMO Command Processor",
            version=importlib.metadata.version("NEMO-Cmd"),
            command_manager=cliff.commandmanager.CommandManager(
                "nemo", convert_underscores=False
            ),
            stderr=sys.stdout,
        )


def main(argv=sys.argv[1:]):
    nemo = NEMO_App()
    return nemo.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
