**********************
NEMO Command Processor
**********************

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0
.. image:: https://img.shields.io/badge/python-3.5+-blue.svg
    :target: https://docs.python.org/3.8/
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
.. image:: https://github.com/SalishSeaCast/NEMO-Cmd/workflows/CI/badge.svg
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/actions?query=workflow%3ACI
    :alt: GitHub Workflow Status
.. image:: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/SalishSeaCast/NEMO-Cmd
    :alt: Codecov Testing Coverage Report
.. image:: https://img.shields.io/github/issues/SalishSeaCast/NEMO-Cmd?logo=github
    :target: https://github.com/SalishSeaCast/NEMO-Cmd/issues
    :alt: Issue Tracker

The NEMO command processor, ``nemo``, is a command line tool for doing various operations associated with running the `NEMO`_ ocean model.

.. _NEMO: http://www.nemo-ocean.eu/

Use ``nemo --help`` to get a list of the sub-commands available.
Use ``nemo help <sub-command>`` to get a synopsis of what a sub-command does,
what its required arguments are,
and what options are available to control it.

Documentation for the command processor is in the ``docs/`` directory and is rendered at https://nemo-cmd.readthedocs.io/en/latest/.

.. image:: https://readthedocs.org/projects/nemo-cmd/badge/?version=latest
    :target: https://nemo-cmd.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

This an extensible tool built on the OpenStack ``cliff``
(`Command Line Interface Formulation Framework`_)
package.
As such,
it can be used as the basis for a NEMO domain-specific command processor tool.

.. _Command Line Interface Formulation Framework: http://docs.openstack.org/developer/cliff/

The ``NEMO-Cmd`` is based on v2.2 of the Salish Sea MEOPAR NEMO model project's ``tools/SalishSeaCmd`` package.


License
=======

.. image:: https://img.shields.io/badge/license-Apache%202-cb2533.svg
    :target: https://www.apache.org/licenses/LICENSE-2.0
    :alt: Licensed under the Apache License, Version 2.0

The NEMO command processor and documentation are copyright 2013-2020 by the `Salish Sea MEOPAR Project Contributors`_ and The University of British Columbia.

.. _Salish Sea MEOPAR Project Contributors: https://bitbucket.org/salishsea/docs/src/tip/CONTRIBUTORS.rst

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
