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

********************************
``NEMO-Cmd`` Package Development
********************************

+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Continuous Integration** | .. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/pytest-with-coverage.yaml/badge.svg                                                                                       |
|                            |      :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:pytest-with-coverage                                                                                              |
|                            |      :alt: Pytest with Coverage Status                                                                                                                                                           |
|                            | .. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/graph/badge.svg?token=ZDCF36TYDQ                                                                                                         |
|                            |      :target: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd                                                                                                                                   |
|                            |      :alt: Codecov Testing Coverage Report                                                                                                                                                       |
|                            | .. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/codeql-analysis.yaml/badge.svg                                                                                            |
|                            |      :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:CodeQL                                                                                                            |
|                            |      :alt: CodeQL analysis                                                                                                                                                                       |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Documentation**          | .. image:: https://app.readthedocs.org/projects/nemo-cmd/badge/?version=latest                                                                                                                   |
|                            |     :target: https://nemo-cmd.readthedocs.io/en/latest/                                                                                                                                          |
|                            |     :alt: Documentation Status                                                                                                                                                                   |
|                            | .. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/sphinx-linkcheck.yaml/badge.svg                                                                                           |
|                            |     :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:sphinx-linkcheck                                                                                                   |
|                            |     :alt: Sphinx linkcheck                                                                                                                                                                       |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Package**                | .. image:: https://img.shields.io/github/v/release/SalishSeaCast/NEMO-Cmd?logo=github                                                                                                            |
|                            |     :target: https://github.com/SalishSeaCast/NEMO-Cmd/releases                                                                                                                                  |
|                            |     :alt: Releases                                                                                                                                                                               |
|                            | .. image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/SalishSeaCast/NEMO-Cmd/main/pyproject.toml&logo=Python&logoColor=gold&label=Python |
|                            |      :target: https://docs.python.org/3/                                                                                                                                                         |
|                            |      :alt: Python Version from PEP 621 TOML                                                                                                                                                      |
|                            | .. image:: https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github                                                                                                               |
|                            |     :target: https://github.com/SalishSeaCast/NEMO-Cmd/issues                                                                                                                                    |
|                            |     :alt: Issue Tracker                                                                                                                                                                          |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Meta**                   | .. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg                                                                                                                            |
|                            |     :target: https://www.apache.org/licenses/LICENSE-2.0                                                                                                                                         |
|                            |     :alt: Licensed under the Apache License, Version 2.0                                                                                                                                         |
|                            | .. image:: https://img.shields.io/badge/version%20control-git-blue.svg?logo=github                                                                                                               |
|                            |     :target: https://github.com/SalishSeaCast/NEMO-Cmd                                                                                                                                           |
|                            |     :alt: Git on GitHub                                                                                                                                                                          |
|                            | .. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white                                                                                          |
|                            |     :target: https://pre-commit.com                                                                                                                                                              |
|                            |     :alt: pre-commit                                                                                                                                                                             |
|                            | .. image:: https://img.shields.io/badge/code%20style-black-000000.svg                                                                                                                            |
|                            |     :target: https://black.readthedocs.io/en/stable/                                                                                                                                             |
|                            |     :alt: The uncompromising Python code formatter                                                                                                                                               |
|                            | .. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg                                                                                                                            |
|                            |     :target: https://github.com/pypa/hatch                                                                                                                                                       |
|                            |     :alt: Hatch project                                                                                                                                                                          |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


.. _NEMO-CmdPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/SalishSeaCast/NEMO-Cmd/main/pyproject.toml&logo=Python&logoColor=gold&label=Python
    :target: https://docs.python.org/3/
    :alt: Python Version from PEP 621 TOML

The :kbd:`NEMO-Cmd` package is developed using `Python`_ 3.14.
The minimum supported Python version is 3.11.
The :ref:`NEMO-CmdContinuousIntegration` workflow on GitHub ensures that the package
is tested for all versions of Python>=3.11.
An old version of the package running under Python 3.5 is deployed on the
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

.. _Conda: https://docs.conda.io/en/latest/
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

.. image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    :target: https://pre-commit.com
    :alt: pre-commit
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The ``NEMO-Cmd`` package uses Git pre-commit hooks managed by `pre-commit`_ to
maintain consistent code style and and other aspects of code,
docs,
and repo QA.

.. _pre-commit: https://pre-commit.com/

To install the `pre-commit` hooks in a newly cloned repo,
activate the conda development environment,
and run :command:`pre-commit install`:

.. code-block:: bash

    $ cd NEMO-Cmd
    $ conda activate nemo-cmd
    (nemo-cmd)$ pre-commit install

.. note::
    You only need to install the hooks once immediately after you make a new clone
    of the `NEMO-Cmd repository`_ and build your :ref:`NEMO-CmdDevelopmentEnvironment`.

.. _NEMO-Cmd repository: https://github.com/SalishSeaCast/NEMO-Cmd


.. _NEMO-CmdBuildingTheDocumentation:

Building the Documentation
==========================

.. image:: https://app.readthedocs.org/projects/nemo-cmd/badge/?version=latest
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

.. _build on readthedocs.org: https://app.readthedocs.org/projects/nemo-cmd/builds/

* build the docs with your changes,
  and preview them in Firefox

* check the docs for broken links


.. _NEMO-CmdBuildingAndPreviewingTheDocumentation:

Building and Previewing the Documentation
-----------------------------------------

Building the documentation is driven by the :file:`docs/Makefile`.
With your :kbd:`nemo-cmd` development environment activated,
use:

.. code-block:: bash

    (nemo-cmd)$ (cd docs && make clean html)

to do a clean build of the documentation.
The output looks something like:

.. code-block:: text

    Removing everything under '_build'...
    Running Sphinx v8.1.3
    loading translations [en]... done
    making output directory... done
    Converting `source_suffix = '.rst'` to `source_suffix = {'.rst': 'restructuredtext'}`.
    loading intersphinx inventory 'python' from https://docs.python.org/3/objects.inv ...
    loading intersphinx inventory 'salishseacmd' from https://salishseacmd.readthedocs.io/en/latest/objects.inv ...
    loading intersphinx inventory 'salishseadocs' from https://salishsea-meopar-docs.readthedocs.io/en/latest/objects.inv ...
    building [mo]: targets for 0 po files that are out of date
    writing output...
    building [html]: targets for 9 source files that are out of date
    updating environment: [new config] 9 added, 0 changed, 0 removed
    reading sources... [100%] subcommands
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    copying assets...
    copying static files...
    Writing evaluated template result to /media/doug/warehouse/MEOPAR/NEMO-Cmd/docs/_build/html/_static/language_data.js
    Writing evaluated template result to /media/doug/warehouse/MEOPAR/NEMO-Cmd/docs/_build/html/_static/basic.css
    Writing evaluated template result to /media/doug/warehouse/MEOPAR/NEMO-Cmd/docs/_build/html/_static/documentation_options.js
    Writing evaluated template result to /media/doug/warehouse/MEOPAR/NEMO-Cmd/docs/_build/html/_static/js/versions.js
    copying static files: done
    copying extra files...
    copying extra files: done
    copying assets: done
    writing output... [100%] subcommands
    generating indices... genindex done
    highlighting module code... [100%] nemo_cmd.prepare
    writing additional pages... search done
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

.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/sphinx-linkcheck.yaml/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:sphinx-linkcheck
    :alt: Sphinx linkcheck

Sphinx also provides a link checker utility which can be run to find broken or redirected links in the docs.
With your :kbd:`nemo-cmd` environment activated,
use:

.. code-block:: bash

    (mohid-cmd)$ cd NEMO-Cmd/docs/
    (mohid-cmd) docs$ make linkcheck

The output looks something like:

.. code-block:: text

    Running Sphinx v8.1.3
    loading translations [en]... done
    making output directory... done
    loading intersphinx inventory 'python' from https://docs.python.org/3/objects.inv ...
    loading intersphinx inventory 'salishseacmd' from https://salishseacmd.readthedocs.io/en/latest/objects.inv ...
    loading intersphinx inventory 'salishseadocs' from https://salishsea-meopar-docs.readthedocs.io/en/latest/objects.inv ...
    building [mo]: targets for 0 po files that are out of date
    writing output...
    building [linkcheck]: targets for 9 source files that are out of date
    updating environment: [new config] 9 added, 0 changed, 0 removed
    reading sources... [100%] subcommands
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    copying assets...
    copying assets: done
    writing output... [100%] subcommands

    (         CHANGES: line   81) ok        https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd
    (         CHANGES: line  114) ok        https://black.readthedocs.io/en/stable/
    (     development: line   36) ok        https://app.readthedocs.org/projects/nemo-cmd/badge/?version=latest
    (     development: line  205) ok        https://app.readthedocs.org/projects/nemo-cmd/builds/
    (run_description_file/3.6_agrif_yaml_file: line   25) ok        https://agrif.imag.fr/
    (         CHANGES: line  199) ok        https://agrif.imag.fr/index.html
    (     development: line   29) ok        https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/graph/badge.svg?token=ZDCF36TYDQ
    (         CHANGES: line  118) ok        https://calver.org/
    (     development: line  449) ok        https://coverage.readthedocs.io/en/latest/
    (     development: line  494) ok        https://docs.github.com/en/actions
    (     development: line  114) ok        https://docs.conda.io/en/latest/miniconda.html
    (         CHANGES: line  179) ok        https://bugs.launchpad.net/python-cliff/+bug/1719465
    (run_description_file/3.6_yaml_file: line  640) ok        https://docs.alliancecan.ca/wiki/Utiliser_des_modules/en
    (     development: line   23) ok        https://docs.python.org/3/
    (run_description_file/3.6_yaml_file: line  197) ok        https://docs.python.org/3/library/constants.html#False
    (     development: line  114) ok        https://docs.conda.io/en/latest/
    (             api: line   98) ok        https://docs.python.org/3/library/constants.html#True
    (             api: line   23) ok        https://docs.python.org/3/library/constants.html#None
    (             api: line   98) ok        https://docs.python.org/3/library/exceptions.html#KeyError
    (     development: line  416) ok        https://docs.pytest.org/en/latest/
    (             api: line   20) ok        https://docs.python.org/3/library/exceptions.html#SystemExit
    (             api: line   23) ok        https://docs.python.org/3/library/functions.html#int
    (             api: line   23) ok        https://docs.python.org/3/library/pathlib.html#pathlib.Path
    (             api: line   45) ok        https://docs.python.org/3/library/stdtypes.html#list
    (             api: line   23) ok        https://docs.python.org/3/library/stdtypes.html#str
    (     subcommands: line  234) ok        https://en.wikipedia.org/wiki/Universally_unique_identifier
    (             api: line   23) ok        https://docs.python.org/3/library/stdtypes.html#dict
    (     development: line  509) ok        https://git-scm.com/
    (         CHANGES: line   95) ok        https://f90nml.readthedocs.io/en/latest/
    (     development: line   26) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/pytest-with-coverage.yaml/badge.svg
    (         CHANGES: line   85) ok        https://github.com/SalishSeaCast/NEMO-Cmd
    (     development: line   39) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/sphinx-linkcheck.yaml/badge.svg
    (     development: line   32) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/codeql-analysis.yaml/badge.svg
    (         CHANGES: line   81) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions
    (     development: line  483) ok        https://github.com/SalishSeaCast/NEMO-Cmd/commits/main
    (     development: line   23) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:CodeQL
    (     development: line   23) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues
    (     development: line   23) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:sphinx-linkcheck
    (         CHANGES: line  253) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/10
    (     development: line   23) ok        https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:pytest-with-coverage
    (         CHANGES: line  249) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/16
    (         CHANGES: line  259) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/11
    (             api: line    6) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/18
    (         CHANGES: line  221) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/19
    (     development: line  537) ok        https://github.com/SalishSeaCast/docs/blob/main/CONTRIBUTORS.rst
    (         CHANGES: line  226) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/20
    (     development: line   23) ok        https://github.com/SalishSeaCast/NEMO-Cmd/releases
    (         CHANGES: line  265) ok        https://github.com/SalishSeaCast/NEMO-Cmd/issues/5
    (         CHANGES: line   41) ok        https://hatch.pypa.io/
    (         CHANGES: line   47) ok        https://github.com/UBC-MOAD/gha-workflows
    (     development: line   65) ok        https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
    (     development: line   62) ok        https://img.shields.io/badge/code%20style-black-000000.svg
    (     development: line   59) ok        https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
    (     development: line   53) ok        https://img.shields.io/badge/license-Apache%202-cb2533.svg
    (    installation: line   36) ok        https://github.com/conda-forge/miniforge
    (     development: line   23) ok        https://github.com/pypa/hatch
    (     development: line   56) ok        https://img.shields.io/badge/version%20control-git-blue.svg?logo=github
    (     development: line   23) ok        https://nemo-cmd.readthedocs.io/en/latest/
    (     development: line   43) ok        https://img.shields.io/github/v/release/SalishSeaCast/NEMO-Cmd?logo=github
    (         CHANGES: line  265) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#grid-section
    (     development: line   46) ok        https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/SalishSeaCast/NEMO-Cmd/main/pyproject.toml&logo=Python&logoColor=gold&label=Python
    (     development: line   49) ok        https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
    (         CHANGES: line  259) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#modules-to-load-section
    (         CHANGES: line  270) ok        https://nemo-cmd.readthedocs.io/en/latest/api.html#functions-for-working-with-file-system-paths
    (         CHANGES: line  229) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#restart-section
    (         CHANGES: line   92) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#vcs-revisions-section
    (         CHANGES: line  253) ok        https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#pbs-resources-section
    (     development: line  130) ok        https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    (run_description_file/index: line   25) ok        https://pyyaml.org/wiki/PyYAMLDocumentation
    (     development: line  449) ok        https://pytest-cov.readthedocs.io/en/latest/
    (run_description_file/3.6_yaml_file: line  190) ok        https://salishsea-meopar-docs.readthedocs.io/en/latest/code-notes/salishsea-nemo/land-processor-elimination/index.html#landprocessorelimination
    (         CHANGES: line  187) ok        https://slurm.schedmd.com/
    (     development: line  156) ok        https://pre-commit.com/
    (     development: line   23) ok        https://pre-commit.com
    (         CHANGES: line  311) ok        https://tox.wiki/en/latest/
    (             api: line   47) ok        https://salishseacmd.readthedocs.io/en/latest/index.html#salishseacmdprocessor
    (     development: line   23) ok        https://www.apache.org/licenses/LICENSE-2.0
    (     development: line   80) ok        https://www.python.org/
    (         CHANGES: line   99) ok        https://ubc-moad-docs.readthedocs.io/en/latest/python_packaging/pkg_structure.html
    (     development: line  189) ok        https://www.sphinx-doc.org/en/master/
    (     development: line  189) ok        https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
    (           index: line   25) ok        https://www.nemo-ocean.eu/
    build succeeded.

    Look for any errors in the above output or in _build/linkcheck/output.txt

:command:`make linkcheck` is run monthly via a `scheduled GitHub Actions workflow`_

.. _scheduled GitHub Actions workflow: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:sphinx-linkcheck


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
The output looks something like:

.. code-block:: text

    ================================== test session starts ===============================
    platform linux -- Python 3.14.0, pytest-8.4.2, pluggy-1.6.0
    Using --randomly-seed=1824633036
    rootdir: /media/doug/warehouse/MEOPAR/NEMO-Cmd
    configfile: pyproject.toml
    plugins: cov-7.0.0, randomly-3.15.0, anyio-4.11.0
    collected 192 items

    tests/test_deflate.py ........                                                  [  4%]
    tests/test_run.py .....................................................         [ 31%]
    tests/test_gather.py .....                                                      [ 34%]
    tests/test_combine.py ............                                              [ 40%]
    tests/test_api.py ........                                                      [ 44%]
    tests/test_prepare.py ................................................................
    .... ......................................                                     [100%]

      ===============================  192 passed in 3.16s ===============================

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

.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/pytest-with-coverage.yaml/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:pytest-with-coverage
    :alt: Pytest with Coverage Status
.. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/graph/badge.svg?token=ZDCF36TYDQ
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


Release Process
===============

.. image:: https://img.shields.io/github/v/release/SalishSeaCast/NEMO-Cmd?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/releases
    :alt: Releases
.. image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
    :target: https://github.com/pypa/hatch
    :alt: Hatch project

Releases are done at Doug's discretion when significant pieces of development work have been
completed.

The release process steps are:

#. Use :command:`hatch version release` to bump the version from ``.devn`` to the next release
   version identifier

#. Edit :file:`docs/CHANGES.rst` to update the version identifier and replace ``unreleased``
   with the release date

#. Commit the version bump and change log update

#. Create and annotated tag for the release with :guilabel:`Git -> New Tag...` in PyCharm
   or :command:`git tag -e -a vyy.n`

#. Push the version bump commit and tag to GitHub

#. Use the GitHub web interface to create a release,
   editing the auto-generated release notes into sections:

   * Features
   * Bug Fixes
   * Documentation
   * Maintenance
   * Dependency Updates

#. Use the GitHub :guilabel:`Issues -> Milestones` web interface to edit the release
   milestone:

   * Change the :guilabel:`Due date` to the release date
   * Delete the "when it's ready" comment in the :guilabel:`Description`

#. Use the GitHub :guilabel:`Issues -> Milestones` web interface to create a milestone for
   the next release:

   * Set the :guilabel:`Title` to the next release version,
     prepended with a ``v``;
     e.g. ``v23.1``
   * Set the :guilabel:`Due date` to the end of the year of the next release
   * Set the :guilabel:`Description` to something like
     ``v23.1 release - when it's ready :-)``
   * Create the next release milestone

#. Review the open issues,
   especially any that are associated with the milestone for the just released version,
   and update their milestone.

#. Close the milestone for the just released version.

#. Use :command:`hatch version minor,dev` to bump the version for the next development cycle,
   or use :command:`hatch version major,minor,dev` for a year rollover version bump

#. Edit :file:`docs/CHANGES.rst` to add a new section for the unreleased dev version

#. Commit the version bump and change log update

#. Push the version bump commit to GitHub
