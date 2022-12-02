**********************
NEMO Command Processor
**********************

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
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:sphinx-linkcheck
    :alt: Sphinx linkcheck
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:pytest-with-coverage
    :alt: Pytest with Coverage Status
.. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/main/graph/badge.svg
    :target: https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd
    :alt: Codecov Testing Coverage Report
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CodeQL/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow:CodeQL
    :alt: CodeQL analysis
.. image:: https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/issues
    :alt: Issue Tracker

The NEMO command processor, ``nemo``, is a command line tool for doing various operations
associated with running the `NEMO`_ ocean model.

.. _NEMO: http://www.nemo-ocean.eu/

Use ``nemo --help`` to get a list of the sub-commands available.
Use ``nemo help <sub-command>`` to get a synopsis of what a sub-command does,
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
it can be used as the basis for a NEMO domain-specific command processor tool.

.. _Command Line Interface Formulation Framework: http://docs.openstack.org/developer/cliff/

The ``NEMO-Cmd`` is based on v2.2 of the SalishSeaCast NEMO model project's
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
