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

Use Pixi to create an isolated environment for :py:obj:`NEMO-Cmd` to avoid conflicts with
other Python packages installed on your system.
That environment will have all of the Python packages necessary to use the :program:`nemo`
command that is provided by the :py:obj:`NEMO-Cmd` package.

.. code-block:: console

    $ cd NEMO-Cmd
    $ pixi install

When you are in the :file:`NEMO-Cmd/` directory
(or a sub-directory)
you can run the :program:`nemo` command with with the :command:`pixi run` command.
Example:

.. code-block:: console

    $ pixi run nemo help

A common use-case is to execute the :command:`nemo run` command in the directory containing
your run description YAML file.
To accomplish that,
we have to tell Pixi where to find the :file:`NEMO-Cmd/` directory so that it can use the
correct environment.
We do that by using the ``-m`` or ``--manifest`` option of :command:`pixi run`.
Example:

.. code-block:: console

    $ cd run_descriptions/
    $ pixi run -m $HOME/MEOPAR/NEMO-Cmd nemo run run_description.yaml \
        /scratch/allen/Carbon/MoreSens/Now/01jan11/

For doing development,
testing,
and documentation of the :py:obj:`NEMO-Cmd` package,
please see the :ref:`NEMO-CmdPackageDevelopment` section.
