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

************************************
:kbd:`NEMO-Cmd` Package Installation
************************************

:kbd:`NEMO-Cmd` is a Python package that provides the :program:`nemo` command-line tool
for doing various operations associated running with the `NEMO`_ ocean model.

.. _NEMO: https://www.nemo-ocean.eu/

These instructions assume that:

* You have an up to date clone of the `NEMO-Cmd package`_ repository.

.. _NEMO-Cmd package: https://github.com/SalishSeaCast/NEMO-Cmd

* You have a `Conda`_ Python environment and package manager
  (`Miniforge`_ or `Miniconda3`_)
  installed

  .. _Conda: https://conda.io/en/latest/
  .. _Miniforge: https://github.com/conda-forge/miniforge
  .. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

To install the :kbd:`NEMO-Cmd` package so that the :command:`nemo` command is available
in your :file:`$HOME/.local/bin/` directory:

.. code-block:: bash

    $ cd NEMO-Cmd
    $ conda env create -f envs/environment-hpc.yaml
    $ conda activate nemo-cmd
    (nemo-cmd)$ python3 -m pip install --user --editable .

The :kbd:`--editable` option in the :command:`pip install` commands installs the package
in a way that it can be updated when new features are pushed to GitHub by simply doing a
:command:`git pull` in the :file:`NEMO-Cmd/` directory.

The :kbd:`Nemo-Cmd` package can also be installed in an isolated :program:`conda` environment.
The common use case for doing so it development,
testing,
and documentation of the package;
please see the :ref:`NEMO-CmdPackageDevelopment` section for details.
