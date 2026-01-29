**********************
NEMO Command Processor
**********************

+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Continuous Integration** | .. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/pytest-with-coverage.yaml/badge.svg                                                                                       |
|                            |      :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:pytest-with-coverage                                                                                              |
|                            |      :alt: Pytest with Coverage Status                                                                                                                                                           |
|                            | .. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/graph/badge.svg?token=ZDCF36TYDQ                                                                                                         |
|                            |      :target: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd                                                                                                                                   |
|                            |      :alt: Codecov Testing Coverage Report                                                                                                                                                       |
|                            | .. image:: https://github.com/SalishSeaCast/NEMO-Cmd/actions/workflows/codeql-analysis.yaml/badge.svg                                                                                            |
|                            |     :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:CodeQL                                                                                                             |
|                            |     :alt: CodeQL analysis                                                                                                                                                                        |
+----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Documentation**          | .. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest                                                                                                                       |
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
|                            | .. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/prefix-dev/pixi/main/assets/badge/v0.json                                                                       |
|                            |     :target: https://pixi.prefix.dev/latest/                                                                                                                                                     |
|                            |     :alt: Pixi                                                                                                                                                                                   |
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

The NEMO command processor, ``nemo``, is a command line tool for doing various operations
associated with running the `NEMO`_ ocean model.

.. _NEMO: http://www.nemo-ocean.eu/

The package uses Pixi_ to manage dependencies and operating environments.
If you don't already have Pixi_ installed,
please follow its `installation instructions`_ to do so.
Please see the `package installation`_ or `package development`_
documentation sections for more details.

.. _Pixi: https://pixi.prefix.dev/latest/
.. _`installation instructions`: https://pixi.prefix.dev/latest/installation/
.. _package installation: https://nemo-cmd.readthedocs.io/en/latest/installation.html
.. _package development: https://nemo-cmd.readthedocs.io/en/latest/pkg_development.html

In the ``NEMO-Cmd/`` directory,
use ``pixi run nemo --help`` to get a list of the sub-commands available.
Use ``pixi run nemo help <sub-command>`` to get a synopsis of what a sub-command does,
what its required arguments are,
and what options are available to control it.

Documentation for the command processor is in the ``docs/`` directory and is rendered
at https://nemo-cmd.readthedocs.io/en/latest/.

.. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
    :target: https://nemo-cmd.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

This an extensible tool built on the OpenStack ``cliff``
(`Command Line Interface Formulation Framework`_)
package.
As such,
it can be used as the basis for domain-specific NEMO command processor tools,
and command processor tools for other ocean models.
Examples:

* `SalishSeaCmd`_: for the SalishSeaCast NEMO configuration
* `AtlantisCmd`_: for the Salish Sea configuration of the `Atlantis`_ marine ecosystem model
* `WWatch3-Cmd`_: for the Salish Sea configuration of the `WAVEWATCH III®`_ wave model
* `MOHID-Cmd`_: for the Salish Sea configuration of the `MOHID`_ oil spill model

.. _Command Line Interface Formulation Framework: http://docs.openstack.org/developer/cliff/
.. _SalishSeaCmd: https://github.com/SalishSeaCast/SalishSeaCmd
.. _AtlantisCmd: https://github.com/SS-Atlantis/AtlantisCmd
.. _Atlantis: https://research.csiro.au/atlantis/
.. _WWatch3-Cmd: https://github.com/SalishSeaCast/WWatch3-Cmd
.. _WAVEWATCH III®: https://polar.ncep.noaa.gov/waves/wavewatch/
.. _MOHID-Cmd: https://github.com/MIDOSS/MOHID-Cmd
.. _MOHID: https://www.mohid.com

The ``NEMO-Cmd`` package is based on v2.2 of the SalishSeaCast NEMO model project's
``tools/SalishSeaCmd`` package.


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
