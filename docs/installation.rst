.. Copyright 2013 – present by the SalishSeaCast contributors
.. and The University of British Columbia
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    https://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

.. SPDX-License-Identifier: Apache-2.0


.. _NEMO-CmdPackageInstallation:

***************************************
:py:obj:`NEMO-Cmd` Package Installation
***************************************

:py:obj:`NEMO-Cmd` is a Python package that provides the :program:`nemo` command-line tool
for doing various operations associated running with the `NEMO`_ ocean model.

.. _NEMO: https://www.nemo-ocean.eu/

These instructions assume that:

* You have an up to date clone of the `NEMO-Cmd package`_ repository.

  .. _NEMO-Cmd package: https://github.com/SalishSeaCast/NEMO-Cmd

* You have installed the Pixi_ package and environments manager
  (`installation instructions`_).

  .. _Pixi: https://pixi.prefix.dev/latest/
  .. _`installation instructions`: https://pixi.prefix.dev/latest/installation/

The packages that are required by :py:obj:`NEMO-Cmd` will be downloaded and linked into
a working environment the first time that you use a `Pixi`_ command in the :file:`MEMO-Cmd/` directory
(or a sub-directory).
Example:

.. code-block:: bash

    cd NEMO-Cmd
    pixi run nemo help

For doing so it development,
testing,
and documentation of the :py:obj:`NEMO-Cmd` package,
please see the :ref:`NEMO-CmdPackageDevelopment` section.
