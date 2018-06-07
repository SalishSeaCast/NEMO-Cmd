**********************
NEMO Command Processor
**********************

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

The NEMO command processor and documentation are copyright 2013-2018 by the Salish Sea MEOPAR Project Contributors and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
https://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.
