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


"""Functions for working with file system paths.

The :func:`fspath` function returns the string representation of a
file system path.
This provides a uniform interface for working with :class:`pathlib.Path`
objects in Python versions both before and after Python 3.6 in which the
PEP 519 file system protocol appeared.

The :func:`resolved_path` function returns an absolute :class:`pathlib.Path`
object with shell and user variables expanded and symlinks resolved.
"""

import os
from pathlib import Path


def fspath(path):
    """Return the string representation of a file system path.

    This function provides a uniform interface for working with
    :class:`pathlib.Path` objects in Python versions both before and after
    Python 3.6 in which the PEP 519 file system protocol appeared.

    :param path: Path to get string representation of.
    :type path: :class:`pathlib.Path` or str

    :return: String representation of path.
    :rtype: str
    """
    return os.fspath(path) if hasattr(os, "fspath") else str(path)


def expanded_path(path):
    """Expand shell and user variables in path and produce a
    :class:`pathlib.Path` object.

    :param path: Path to expand variables in.
    :type path: :class:`pathlib.Path` or str

    :return: Path with shell and user variables expanded.
    :rtype: :class:`pathlib.Path`
    """
    return Path(os.path.expandvars(fspath(path))).expanduser()


def resolved_path(path):
    """Expand shell and user variables in path and resolve symbolic links
    to produce an absolute :class:`pathlib.Path` object.

    :param path: Path to expand variables in and resolve.
    :type path: :class:`pathlib.Path` or str

    :return: Absolute path with shell and user variables expanded and
             symlinks resolved.
    :rtype: :class:`pathlib.Path`
    """
    return expanded_path(path).resolve()
