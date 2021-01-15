.. Copyright 2013-2021 The Salish Sea MEOPAR contributors
.. and The University of British Columbia
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..    http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


.. _NEMO-CmdPackageInstallation:

************************************
:kbd:`NEMO-Cmd` Package Installation
************************************

:kbd:`NEMO-Cmd` is a Python package that provides the :program:`nemo` command-line tool for doing various operations associated running with the `NEMO`_ ocean model.

.. _NEMO: https://www.nemo-ocean.eu/

These instructions assume that:

* You have an up to date clone of the `NEMO-Cmd package`_ repository.

.. _NEMO-Cmd package: https://github.com/SalishSeaCast/NEMO-Cmd

* You have the `Anaconda Python Distribution`_ or `Miniconda3`_ installed

.. _Anaconda Python Distribution: https://www.anaconda.com/products/individual
.. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

* :file:`$HOME/anaconda3/bin` is included in your :envvar:`PATH` environment variable if you are using the Anaconda,
  or :file:`$HOME/miniconda3/bin` is included in your :envvar:`PATH` environment variable if you are using Miniconda

To install the :kbd:`NEMO-Cmd` package in your :kbd:`root` Anaconda or Miniconda environment use:

.. code-block:: bash

    $ cd NEMO-Cmd
    $ pip install --user --editable .

The :kbd:`--editable` option in the :command:`pip install` commands installs the packages via symlinks so that :program:`nemo` will be automatically updated as the repo evolves.

The :kbd:`Nemo-Cmd` package can also be installed in an isolated :program:`conda` environment.
The common use case for doing so it development,
testing,
and documentation of the package;
please see the :ref:`NEMO-CmdPackageDevelopment` section for details.


.. _nemoTabCompletion:

:kbd:`<TAB>` Completion
=======================

.. note::

    :kbd:`<TAB>` completion is only available in recent versions of :command:`bash`.
    The instructions below are only useful if you are working on Ubuntu 14.04 or later.

The :program:`nemo` command line interface includes a sub-command that enables it to hook into the :program:`bash` :kbd:`<TAB>` completion machinery.
(:kbd:`<TAB>` completion or `command-line completion`_ is a shell feature whereby partially typed commands are filled out by the shell when the user presses the :kbd:`<TAB>` key.)
The :command:`nemo complete` command prints a blob of :program:`bash` code that does the job,
so,
capturing that code and executing it with the :command:`eval` command will enable completion for :program:`nemo` in your current shell session.
You can do that with the compound command:

.. code-block:: bash

    eval "$(nemo complete)"

Including that line in your :file:`~/.bashrc` file will ensure that completion for :program:`nemo` is available in every shell you launch.

.. _command-line completion: https://en.wikipedia.org/wiki/Command-line_completion
