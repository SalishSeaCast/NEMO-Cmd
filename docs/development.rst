.. Copyright 2013-2019 The Salish Sea MEOPAR contributors
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


.. _NEMO-CmdPackageDevelopment:

***********************************
:kbd:`NEMO-Cmd` Package Development
***********************************

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.5+-blue.svg
    :target: https://docs.python.org/3.7/
    :alt: Python Version
.. image:: https://img.shields.io/badge/version%20control-hg-blue.svg
    :target: https://bitbucket.org/salishsea/nemo-cmd/
    :alt: Mercurial on Bitbucket
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter
.. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
    :target: https://nemo-cmd.readthedocs.io/en/latest/
    :alt: Documentation Status
.. image:: https://img.shields.io/bitbucket/issues/salishsea/nemo-cmd.svg
    :target: https://bitbucket.org/salishsea/nemo-cmd/issues?status=new&status=open
    :alt: Issue Tracker


.. _NEMO-CmdPythonVersions:

Python Versions
===============

.. image:: https://img.shields.io/badge/python-3.5+-blue.svg
    :target: https://docs.python.org/3.7/
    :alt: Python Version

The :kbd:`NEMO-Cmd` package is developed and tested using `Python`_ 3.7.
However,
the package must also run under `Python`_ 3.5 for use on the Westgrid :kbd:`orcinus` HPC platform.


.. _NEMO-CmdGettingTheCode:

Getting the Code
================

.. image:: https://img.shields.io/badge/version%20control-hg-blue.svg
    :target: https://bitbucket.org/salishsea/nemo-cmd/
    :alt: Mercurial on Bitbucket

Clone the code and documentation `repository`_ from Bitbucket with:

.. _repository: https://bitbucket.org/salishsea/nemo-cmd/

.. code-block:: bash

    $ hg clone ssh://hg@bitbucket.org/salishsea/nemo-cmd/

or

.. code-block:: bash

    $ hg clone https://<your_userid>@bitbucket.org/salishsea/nemo-cmd/

if you don't have `ssh key authentication`_ set up on Bitbucket.

.. _ssh key authentication: https://confluence.atlassian.com/bitbucket/set-up-ssh-for-mercurial-728138122.html


.. _NEMO-CmdDevelopmentEnvironment:

Development Environment
=======================

Setting up an isolated development environment using `Conda`_ is recommended.
Assuming that you have `Anaconda Python Distribution`_ or `Miniconda3`_ installed,
you can create and activate an environment called :kbd:`nemo-cmd` that will have all of the Python packages necessary for development,
testing,
and building the documentation with the commands:

.. _Python: https://www.python.org/
.. _Conda: http://conda.pydata.org/docs/
.. _Anaconda Python Distribution: http://www.continuum.io/downloads
.. _Miniconda3: http://conda.pydata.org/docs/install/quick.html

.. code-block:: bash

    $ cd NEMO-Cmd
    $ conda env create -f env/environment-dev.yaml
    $ source activate nemo-cmd
    (nemo-cmd)$ pip install --editable .

The :kbd:`--editable` option in the :command:`pip install` commands above installs the :kbd:`NEMO-Cmd` package from the repository clone via symlinks so that :program:`nemo` command in the :kbd:`nemo-cmd` environment will be automatically updated as the repo evolves.

To deactivate the environment use:

.. code-block:: bash

    (nemo-cmd)$ source deactivate


.. _NEMO-CmdCodingStyle:

Coding Style
============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://black.readthedocs.io/en/stable/
    :alt: The uncompromising Python code formatter

The :kbd:`NEMO-Cmd` package uses the `black`_ code formatting tool to maintain a coding style that is very close to `PEP 8`_.

.. _black: https://black.readthedocs.io/en/stable/
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/

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
Creating a :ref:`NEMO-CmdDevelopmentEnvironment` as described above includes the installation of Sphinx.
Building the documentation is driven by :file:`tools/docs/Makefile`.
With your :kbd:`nemo-cmd` development environment activated,
use:

.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _Sphinx: http://sphinx-doc.org/

.. code-block:: bash

    (nemo-cmd)$ cd tools
    (nemo-cmd)$ (cd docs && make clean html)

to do a clean build of the documentation.
The output looks something like::

  rm -rf _build/*
  sphinx-build -b html -d _build/doctrees   . _build/html
  Running Sphinx v1.5.1
  making output directory...
  loading pickled environment... not yet created
  loading intersphinx inventory from https://docs.python.org/3/objects.inv...
  building [mo]: targets for 0 po files that are out of date
  building [html]: targets for 9 source files that are out of date
  updating environment: 9 added, 0 changed, 0 removed
  reading sources... [100%] subcommands
  looking for now-outdated files... none found
  pickling environment... done
  checking consistency... done
  preparing documents... done
  writing output... [100%] subcommands
  generating indices... genindex
  highlighting module code... [100%] nemo_cmd.prepare
  writing additional pages... search
  copying static files... done
  copying extra files... done
  dumping search index in English (code: en) ... done
  dumping object inventory... done
  build succeeded.

  Build finished. The HTML pages are in _build/html.

The HTML rendering of the docs ends up in :file:`NEMO-Cmd/docs/_build/html/`.
You can open the :file:`index.html` file in that directory tree in your browser to preview the results of the build before committing and pushing your changes to Bitbucket.

Whenever you push changes to the :kbd:`NEMO-Cmd` repository on Bitbucket the documentation is automatically re-built and rendered at https://nemo-cmd.readthedocs.io/en/latest/.


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
    (salishsea-cmd)$ py.test

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

You can monitor what lines of code the test suite exercises using the `coverage.py`_ tool with the command:

.. _coverage.py: https://coverage.readthedocs.io/en/latest/

.. code-block:: bash

    (salishsea-cmd)$ cd NEMO-Cmd/
    (salishsea-cmd)$ coverage run -m py.test

and generate a test coverage report with:

.. code-block:: bash

    (salishsea-cmd)$ coverage report

to produce a plain text report,
or

.. code-block:: bash

    (salishsea-cmd)$ coverage html

to produce an HTML report that you can view in your browser by opening :file:`NEMO-Cmd/htmlcov/index.html`.


Continuous Integration
----------------------

The :kbd:`NEMO-Cmd` package unit test suite is run and a coverage report is generated whenever changes are pushed to Bitbucket.
The results are visible on the `repo pipelines page`_,
from the :guilabel:`Builds` column on the `repo commits page`_,
or from a link in the build status area on the right side of the `repo summary page`_ .

.. _repo pipelines page: https://bitbucket.org/salishsea/nemo-cmd/addon/pipelines/home
.. _repo commits page: https://bitbucket.org/salishsea/nemo-cmd/commits/all
.. _repo summary page: https://bitbucket.org/salishsea/nemo-cmd/


Pipelines Container Image
^^^^^^^^^^^^^^^^^^^^^^^^^

The Bitbucket pipelines configuration in :file:`bitbucket-pipelines.yml` uses a custom image that includes a :command:`conda` environment for running the test wuite with coverage analysis.
The image is defined and maintained using the :file:`Dockerfile` and :file:`environment-test.yaml` files in the :file:`pipelines-test-env/` directory.

To build or update the image and push it to Docker Hub use:

.. code-block:: bash

    docker build -t nemo-cmd-test pipelines-test-env/
    docker tag nemo-cmd-test:latest douglatornell/salishsea:nemo-cmd-test
    docker push douglatornell/salishsea:nemo-cmd-test


.. _NEMO-CmdVersionControlRepository:

Version Control Repository
==========================

.. image:: https://img.shields.io/badge/version%20control-hg-blue.svg
    :target: https://bitbucket.org/salishsea/nemo-cmd/
    :alt: Mercurial on Bitbucket

The :kbd:`NEMO-Cmd` package code and documentation source files are available from the `Mercurial`_ repository at https://bitbucket.org/salishsea/nemo-cmd.


.. _NEMO-CmdIssueTracker:

Issue Tracker
=============

.. image:: https://img.shields.io/bitbucket/issues/salishsea/nemo-cmd.svg
    :target: https://bitbucket.org/salishsea/nemo-cmd/issues?status=new&status=open
    :alt: Issue Tracker

Development tasks,
bug reports,
and enhancement ideas are recorded and managed in the issue tracker at https://bitbucket.org/salishsea/nemo-cmd/issues.


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The NEMO command processor and documentation are Copyright 2013-2019 by the Salish Sea MEOPAR Project Contributors and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
