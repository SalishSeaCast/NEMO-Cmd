# Copyright 2013-2021 The Salish Sea MEOPAR Contributors
# and The University of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
__version__ = "21.1.dev0"


# Make fspath.fspath() and fspath.resolved_path() available in the nemo_cmd
# namespace
from nemo_cmd.fspath import fspath, expanded_path, resolved_path
