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


.. _NEMO-CmdPackageDevelopment:

***********************************
:kbd:`NEMO-Cmd` Package Development
***********************************

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
    :target: https://docs.python.org/3.11/
    :alt: Python Version
.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd
    :alt: Git on GitHub
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter
.. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
    :target: https://nemo-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/sphinx-linkcheck/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3A
    :alt: Sphinx linkcheck
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3ACI
    :alt: GitHub Workflow Status
.. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd
    :alt: Codecov Testing Coverage Report
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CodeQL/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:CodeQL
    :alt: CodeQL analysis
.. image:: https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/issues
    :alt: Issue Tracker


.. _NEMO-CmdPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
    :target: https://docs.python.org/3.11/
    :alt: Python Version

The :kbd:`NEMO-Cmd` package is developed using `Python`_ 3.11.
The minimum supported Python version is 3.8.
The :ref:`NEMO-CmdContinuousIntegration` workflow on GitHub ensures that the package
is tested for all versions of Python>=3.8.
An old version of the package running under Python 3.5 is depoloyed on the
Westgrid :kbd:`orcinus` HPC platform.
That version is tagged in the repository as ``orcinus-python-3.5``.

.. _Python: https://www.python.org/


.. _NEMO-CmdGettingTheCode:

Getting the Code
================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd
    :alt: Git on GitHub

Clone the code and documentation `repository`_ from GitHub with:

.. _repository: https://github.com/SalishSeaCast/NEMO-Cmd

.. code-block:: bash

    $ git clone git@github.com:SalishSeaCast/NEMO-Cmd.git


.. _NEMO-CmdDevelopmentEnvironment:

Development Environment
=======================

Setting up an isolated development environment using `Conda`_ is recommended.
Assuming that you have `Miniconda3`_ installed,
you can create and activate an environment called ``nemo-cmd`` that will have
all of the Python packages necessary for development,
testing,
and building the documentation with the commands below.

.. _Conda: https://conda.io/en/latest/
.. _Miniconda3: https://docs.conda.io/en/latest/miniconda.html

.. code-block:: bash

    $ cd NEMO-Cmd
    $ conda env create -f envs/environment-dev.yaml
    $ conda activate nemo-cmd

:kbd:`NEMO-Cmd` is installed in `editable install mode`_ as part of the conda environment
creation process.
That means that the package is installed from the cloned repo via symlinks so that
it will be automatically updated as the repo evolves.

.. _editable install mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

To deactivate the environment use:

.. code-block:: bash

    (nemo-cmd)$ conda deactivate


.. _NEMO-CmdCodingStyle:

Coding Style
============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The :kbd:`NEMO-Cmd` package uses the `black`_ code formatting tool to maintain a coding style that is very close to `PEP 8`_.

.. _black: https://black.readthedocs.io/en/stable/
.. _PEP 8: https://peps.python.org/pep-0008/

:command:`black` is installed as part of the :ref:`NEMO-CmdDevelopmentEnvironment` setup.

To run :command:`black` on the entire code-base use:

.. code-block:: bash

    $ cd NEMO-Cmd
    $ conda activate nemo-cmd
    (nemo-cmd)$ black ./

in the repository root directory.
The output looks something like::

  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/nemo_cmd/fspath.py
  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/tests/test_api.py
  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/nemo_cmd/run.py
  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/tests/test_run.py
  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/nemo_cmd/prepare.py
  reformatted /media/doug/warehouse/MEOPAR/NEMO-Cmd/tests/test_prepare.py
  All done! ✨ 🍰 ✨
  6 files reformatted, 14 files left unchanged.


.. _NEMO-CmdBuildingTheDocumentation:

Building the Documentation
==========================

.. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
    :target: https://nemo-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status

The documentation for the :kbd:`NEMO-Cmd` package is written in `reStructuredText`_ and converted to HTML using `Sphinx`_.

.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/

If you have write access to the `repository`_ on GitHub,
whenever you push changes to GitHub the documentation is automatically re-built and rendered at https://nemo-cmd.readthedocs.io/en/latest/.

Additions,
improvements,
and corrections to these docs are *always* welcome.

The quickest way to fix typos, etc. on existing pages is to use the :guilabel:`Edit on GitHub` link in the upper right corner of the page to get to the online editor for the page on `GitHub`_.

.. _GitHub: https://github.com/SalishSeaCast/NEMO-Cmd

For more substantial work,
and to add new pages,
follow the instructions in the :ref:`NEMO-CmdDevelopmentEnvironment` section above.
In the development environment you can build the docs locally instead of having to push commits to GitHub to trigger a `build on readthedocs.org`_ and wait for it to complete.
Below are instructions that explain how to:

.. _build on readthedocs.org: https://readthedocs.org/projects/nemo-cmd/builds/

* build the docs with your changes,
  and preview them in Firefox

* check the docs for broken links


.. _NEMO-CmdBuildingAndPreviewingTheDocumentation:

Building and Previewing the Documentation
-----------------------------------------

Building the documentation is driven by the :file:`docs/Makefile`.
With your :kbd:`mohid-cmd` development environment activated,
use:

.. code-block:: bash

    (nemo-cmd)$ (cd docs && make clean html)

to do a clean build of the documentation.
The output looks something like::

  Removing everything under '_build'...
  Running Sphinx v3.3.0
  making output directory... done
  loading intersphinx inventory from https://docs.python.org/3/objects.inv...
  loading intersphinx inventory from https://salishseacmd.readthedocs.io/en/latest/objects.inv...
  loading intersphinx inventory from https://salishsea-meopar-docs.readthedocs.io/en/latest/objects.inv...
  building [mo]: targets for 0 po files that are out of date
  building [html]: targets for 9 source files that are out of date
  updating environment: [new config] 9 added, 0 changed, 0 removed
  reading sources... [100%] subcommands
  looking for now-outdated files... none found
  pickling environment... done
  checking consistency... done
  preparing documents... done
  writing output... [100%] subcommands
  generating indices... genindex done
  highlighting module code... [100%] nemo_cmd.prepare
  writing additional pages... search done
  copying static files... done
  copying extra files... done
  dumping search index in English (code: en)... done
  dumping object inventory... done
  build succeeded.

  The HTML pages are in _build/html.

The HTML rendering of the docs ends up in :file:`NEMO-Cmd/docs/_build/html/`.
You can open the :file:`index.html` file in that directory tree in your browser to preview the results of the build before committing and pushing your changes to GitHub.

Whenever you push changes to the :kbd:`NEMO-Cmd` repository on GitHub the documentation is automatically re-built and rendered at https://nemo-cmd.readthedocs.io/en/latest/.


.. _NEMO-CmdLinkCheckingTheDocumentation:

Link Checking the Documentation
-------------------------------

.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/sphinx-linkcheck/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3A
    :alt: Sphinx linkcheck

Sphinx also provides a link checker utility which can be run to find broken or redirected links in the docs.
With your :kbd:`nemo-cmd` environment activated,
use:

.. code-block:: bash

    (mohid-cmd)$ cd NEMO-Cmd/docs/
    (mohid-cmd) docs$ make linkcheck

The output looks something like::

  Running Sphinx v3.3.0
  making output directory... done
  loading intersphinx inventory from https://docs.python.org/3/objects.inv...
  loading intersphinx inventory from https://salishseacmd.readthedocs.io/en/latest/objects.inv...
  loading intersphinx inventory from https://salishsea-meopar-docs.readthedocs.io/en/latest/objects.inv...
  building [mo]: targets for 0 po files that are out of date
  building [linkcheck]: targets for 9 source files that are out of date
  updating environment: [new config] 9 added, 0 changed, 0 removed
  reading sources... [100%] subcommands
  looking for now-outdated files... none found
  pickling environment... done
  checking consistency... done
  preparing documents... done
  writing output... [ 11%] CHANGES
  (line   23) ok        https://f90nml.readthedocs.io/en/latest/
  (line   20) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#vcs-revisions-section
  (line   27) ok        https://ubc-moad-docs.readthedocs.io/en/latest/python_packaging/pkg_structure.html
  (line   42) ok        https://black.readthedocs.io/en/stable/
  (line    9) ok        https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd
  (line  115) ok        https://slurm.schedmd.com/
  (line   46) ok        https://calver.org/
  (line  127) ok        http://agrif.imag.fr/
  (line  107) ok        https://bugs.launchpad.net/python-cliff/+bug/1719465
  (line  157) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#restart-section
  (line    9) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions
  (line  181) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#pbs-resources-section
  (line   13) ok        https://github.com/SalishSeaCast/NEMO-Cmd
  (line  187) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#modules-to-load-section
  (line  177) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/16
  (line  193) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#grid-section
  (line  149) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/19
  (line  198) ok        https://nemo-cmd.readthedocs.io/en/latest/api.html#functions-for-working-with-file-system-paths
  (line  239) ok        https://tox.wiki/en/latest/
  (line  154) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/20
  (line  187) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/11
  (line  181) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/10
  (line  193) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/5
  writing output... [ 22%] api
  (line   21) ok        https://docs.python.org/3/library/pathlib.html#pathlib.Path
  (line   21) ok        https://docs.python.org/3/library/pathlib.html#pathlib.Path
  (line   21) ok        https://docs.python.org/3/library/pathlib.html#pathlib.Path
  (line   21) ok        https://docs.python.org/3/library/functions.html#int
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#str
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#str
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#str
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#str
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#str
  (line   21) ok        https://docs.python.org/3/library/constants.html#None
  (line   21) ok        https://docs.python.org/3/library/constants.html#None
  (line   21) ok        https://docs.python.org/3/library/constants.html#None
  (line   45) ok        https://salishseacmd.readthedocs.io/en/latest/index.html#salishseacmdprocessor
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#dict
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#dict
  (line   20) ok        https://docs.python.org/3/library/exceptions.html#SystemExit
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#dict
  (line   21) ok        https://docs.python.org/3/library/stdtypes.html#dict
  (line   11) ok        https://docs.python.org/3/library/exceptions.html#SystemExit
  (line   96) ok        https://docs.python.org/3/library/constants.html#True
  (line   43) ok        https://docs.python.org/3/library/stdtypes.html#dict
  (line   96) ok        https://docs.python.org/3/library/constants.html#True
  (line   43) ok        https://docs.python.org/3/library/stdtypes.html#list
  (line   29) ok        https://docs.python.org/3/library/exceptions.html#KeyError
  (line   96) ok        https://docs.python.org/3/library/exceptions.html#KeyError
  (line    6) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/18
  writing output... [ 33%] development
  (line   21) ok        https://docs.python.org/3.11/
  (line   21) ok        https://nemo-cmd.readthedocs.io/en/latest/
  (line   61) ok        https://www.python.org/
  (line   95) ok        https://conda.io/en/latest/
  (line   21) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues
  (line   21) ok        https://www.apache.org/licenses/LICENSE-2.0
  (line   95) ok        https://docs.conda.io/en/latest/miniconda.html
  (line  131) ok        https://peps.python.org/pep-0008/
  (line   21) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3ACI
  (line  168) ok        https://www.sphinx-doc.org/en/master/
  (line  168) ok        https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
  (line   21) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3A
  (line  392) ok        https://docs.pytest.org/en/latest/
  (line  425) ok        https://coverage.readthedocs.io/en/latest/
  (line  425) ok        https://pytest-cov.readthedocs.io/en/latest/
  (line  184) ok        https://readthedocs.org/projects/nemo-cmd/builds/
  (line  470) ok        https://docs.github.com/en/actions
  (line  249) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3A
  (line  484) ok        https://git-scm.com/
  (line   21) ok        https://img.shields.io/badge/license-Apache%202-cb2533.svg
  (line   21) ok        https://img.shields.io/badge/python-3.8+-blue.svg
  (line   21) ok        https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
  (line   21) ok        https://img.shields.io/badge/code%20style-black-000000.svg
  (line  382) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3Asphinx-linkcheck
  (line   21) ok        https://github.com/SalishSeaCast/NEMO-Cmd/workflows/sphinx-linkcheck/badge.svg
  (line   21) ok        https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
  (line  510) ok        https://github.com/SalishSeaCast/docs/blob/main/CONTRIBUTORS.rst
  (line   21) ok        https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
  (line   21) ok        https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/main/graph/badge.svg
  (line  450) ok        https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/main/graph/badge.svg
  (line  459) ok        https://github.com/SalishSeaCast/NEMO-Cmd/commits/main
  (line  450) ok        https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
  (line   21) ok        https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
  (line  492) ok        https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
  writing output... [ 44%] index
  (line   58) ok        https://www.apache.org/licenses/LICENSE-2.0
  (line   23) ok        https://www.nemo-ocean.eu/
  writing output... [ 55%] installation
  (line   67) ok        https://en.wikipedia.org/wiki/Command-line_completion
  writing output... [ 66%] run_description_file/3.6_agrif_yaml_file
  writing output... [ 77%] run_description_file/3.6_yaml_file
  (line  195) ok        https://docs.python.org/3/library/constants.html#False
  (line  458) ok        https://docs.python.org/3/library/constants.html#False
  (line  195) ok        https://salishsea-meopar-docs.readthedocs.io/en/latest/code-notes/salishsea-nemo/land-processor-elimination/index.html#landprocessorelimination
  (line  188) ok        https://salishsea-meopar-docs.readthedocs.io/en/latest/code-notes/salishsea-nemo/land-processor-elimination/index.html#landprocessorelimination
  (line  641) ok        http://modules.sourceforge.net/
  writing output... [ 88%] run_description_file/index
  (line   23) ok        https://pyyaml.org/wiki/PyYAMLDocumentation
  writing output... [100%] subcommands
  (line  232) ok        https://en.wikipedia.org/wiki/Universally_unique_identifier

  build succeeded.

  Look for any errors in the above output or in _build/linkcheck/output.txt

:command:`make linkcheck` is run monthly via a `scheduled GitHub Actions workflow`_

.. _scheduled GitHub Actions workflow: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3Asphinx-linkcheck


.. _NEMO-CmdRuningTheUnitTests:

Running the Unit Tests
======================

The test suite for the :kbd:`NEMO-Cmd` package is in :file:`NEMO-Cmd/tests/`.
The `pytest`_ tools is used for test fixtures and as the test runner for the suite.

.. _pytest: https://docs.pytest.org/en/latest/

With your :kbd:`nemo-cmd` development environment activated,
use:

.. _Mercurial: https://www.mercurial-scm.org/

.. code-block:: bash

    (salishsea-cmd)$ cd NEMO-Cmd/
    (salishsea-cmd)$ pytest

to run the test suite.
The output looks something like::

  =========================== test session starts =============================
  platform linux -- Python 3.6.1, pytest-3.0.5, py-1.4.32, pluggy-0.4.0
  rootdir: /media/doug/warehouse/MEOPAR/NEMO-Cmd, inifile:
  collected 166 items

  tests/test_api.py ........
  tests/test_combine.py ............
  tests/test_deflate.py ...
  tests/test_gather.py ...
  tests/test_namelist.py .............
  tests/test_prepare.py .....................................................................................
  tests/test_run.py ..........................................

  ======================== 166 passed in 1.68 seconds ========================

You can monitor what lines of code the test suite exercises using the `coverage.py`_ and `pytest-cov`_ tools with the command:

.. _coverage.py: https://coverage.readthedocs.io/en/latest/
.. _pytest-cov: https://pytest-cov.readthedocs.io/en/latest/

.. code-block:: bash

    (salishsea-cmd)$ cd NEMO-Cmd/
    (salishsea-cmd)$ pytest --cov=./

The test coverage report will be displayed below the test suite run output.

Alternatively,
you can use

.. code-block:: bash

    (salishsea-cmd)$ pytest --cov=./ --cov-report html

to produce an HTML report that you can view in your browser by opening :file:`NEMO-Cmd/htmlcov/index.html`.


.. _NEMO-CmdContinuousIntegration:

Continuous Integration
----------------------

.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3ACI
    :alt: GitHub Workflow Status
.. image:: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd
    :alt: Codecov Testing Coverage Report

The :kbd:`NEMO-Cmd` package unit test suite is run and a coverage report is generated whenever changes are pushed to GitHub.
The results are visible on the `repo actions page`_,
from the green checkmarks beside commits on the `repo commits page`_,
or from the green checkmark to the left of the "Latest commit" message on the `repo code overview page`_ .
The testing coverage report is uploaded to `codecov.io`_

.. _repo actions page: https://github.com/SalishSeaCast/NEMO-Cmd/actions
.. _repo commits page: https://github.com/SalishSeaCast/NEMO-Cmd/commits/main
.. _repo code overview page: https://github.com/SalishSeaCast/NEMO-Cmd
.. _codecov.io: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd

The `GitHub Actions`_ workflow configuration that defines the continuous integration
tasks is in the :file:`.github/workflows/pytest-coverage.yaml` file.

.. _GitHub Actions: https://docs.github.com/en/actions


.. _NEMO-CmdVersionControlRepository:

Version Control Repository
==========================

.. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd
    :alt: Git on GitHub

The :kbd:`NEMO-Cmd` package code and documentation source files are available from
the `Git`_ repository at https://github.com/SalishSeaCast/NEMO-Cmd.

.. _Git: https://git-scm.com/


.. _NEMO-CmdIssueTracker:

Issue Tracker
=============

.. image:: https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/issues
    :alt: Issue Tracker

Development tasks,
bug reports,
and enhancement ideas are recorded and managed in the issue tracker
at https://github.com/SalishSeaCast/NEMO-Cmd/issues.


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The NEMO command processor and documentation are copyright 2013 – present
by the `SalishSeaCast Project Contributors`_ and The University of British Columbia.

.. _SalishSeaCast Project Contributors: https://github.com/SalishSeaCast/docs/blob/main/CONTRIBUTORS.rst

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
