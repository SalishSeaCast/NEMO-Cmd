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


.. _NEMO-CmdSubcommands:

****************************
:command:`nemo` Sub-Commands
****************************

The command :kbd:`nemo help` produces a list of the available :program:`nemo` options and sub-commands::

  usage: nemo [--version] [-v | -q] [--log-file LOG_FILE] [-h] [--debug]

  NEMO Command Processor

  optional arguments:
    --version            show program's version number and exit
    -v, --verbose        Increase verbosity of output. Can be repeated.
    -q, --quiet          Suppress output except warnings and errors.
    --log-file LOG_FILE  Specify a file to log output. Disabled by default.
    -h, --help           Show help message and exit.
    --debug              Show tracebacks on errors.

  Commands:
    combine        Combine per-processor files from an MPI NEMO run into single files
    complete       print bash completion command
    deflate        Deflate variables in netCDF files using Lempel-Ziv compression.
    gather         Gather results from a NEMO run.
    help           print detailed help for another command
    prepare        Prepare a NEMO run
    run            Prepare, execute, and gather results from a NEMO model run.

For details of the arguments and options for a sub-command use
:command:`nemo help <sub-command>`.
For example:

.. code-block:: bash

    $ nemo help run

::

    usage: nemo run [-h] [--max-deflate-jobs MAX_DEFLATE_JOBS]
                    [--nocheck-initial-conditions] [--no-deflate] [--no-submit]
                    [--waitjob WAITJOB] [--queue-job-cmd {qsub,sbatch}] [-q]
                    DESC_FILE RESULTS_DIR

    Prepare, execute, and gather the results from a NEMO run described in
    DESC_FILE. The results files from the run are gathered in RESULTS_DIR. If
    RESULTS_DIR does not exist it will be created.

    positional arguments:
      DESC_FILE             run description YAML file
      RESULTS_DIR           directory to store results into

    optional arguments:
      -h, --help            show this help message and exit
      --max-deflate-jobs MAX_DEFLATE_JOBS
                            Maximum number of concurrent sub-processes to use for
                            netCDF deflating. Defaults to 4.
      --nocheck-initial-conditions
                            Suppress checking of the initial conditions link.
                            Useful if you are submitting a job to wait on a
                            previous job
      --no-deflate          Do not include "nemo deflate" command in the bash
                            script. Use this option if you are using on-the-fly
                            deflation in XIOS-2; i.e. you are using 1 XIOS-2
                            process and have the compression_level="4" attribute
                            set in all of the file_group definitions in your
                            file_def.xml file.
      --no-submit           Prepare the temporary run directory, and the bash
                            script to execute the NEMO run, but don't submit the
                            run to the queue. This is useful during development
                            runs when you want to hack on the bash script and/or
                            use the same temporary run directory more than once.
      --waitjob WAITJOB     use -W waitjob in call to qsub, to make current job
                            wait for on waitjob. Waitjob is the queue job number
      --queue-job-cmd {qsub,sbatch}
                            Command to use to submit the bash script to execute
                            the NEMO run; defaults to qsub.
      -q, --quiet           don't show the run directory path or job submission
                            message

You can check what version of :program:`nemo` you have installed with:

.. code-block:: bash

    nemo --version


.. _nemo-run:

:kbd:`run` Sub-command
======================

The :command:`run` sub-command prepares,
executes,
and gathers the results from the NEMO run described in the specified run description file.
The results are gathered in the specified results directory.

::

    usage: nemo run [-h] [--max-deflate-jobs MAX_DEFLATE_JOBS]
                    [--nocheck-initial-conditions] [--no-deflate] [--no-submit]
                    [--waitjob WAITJOB] [--queue-job-cmd {qsub,sbatch}] [-q]
                    DESC_FILE RESULTS_DIR

    Prepare, execute, and gather the results from a NEMO run described in
    DESC_FILE. The results files from the run are gathered in RESULTS_DIR. If
    RESULTS_DIR does not exist it will be created.

    positional arguments:
      DESC_FILE             run description YAML file
      RESULTS_DIR           directory to store results into

    optional arguments:
      -h, --help            show this help message and exit
      --max-deflate-jobs MAX_DEFLATE_JOBS
                            Maximum number of concurrent sub-processes to use for
                            netCDF deflating. Defaults to 4.
      --nocheck-initial-conditions
                            Suppress checking of the initial conditions link.
                            Useful if you are submitting a job to wait on a
                            previous job
      --no-deflate          Do not include "nemo deflate" command in the bash
                            script. Use this option if you are using on-the-fly
                            deflation in XIOS-2; i.e. you are using 1 XIOS-2
                            process and have the compression_level="4" attribute
                            set in all of the file_group definitions in your
                            file_def.xml file.
      --no-submit           Prepare the temporary run directory, and the bash
                            script to execute the NEMO run, but don't submit the
                            run to the queue. This is useful during development
                            runs when you want to hack on the bash script and/or
                            use the same temporary run directory more than once.
      --waitjob WAITJOB     use -W waitjob in call to qsub, to make current job
                            wait for on waitjob. Waitjob is the queue job number
      --queue-job-cmd {qsub,sbatch}
                            Command to use to submit the bash script to execute
                            the NEMO run; defaults to qsub.
      -q, --quiet           don't show the run directory path or job submission
                            message

The path to the run directory,
and the response from the job queue manager
(typically a job number)
are printed upon completion of the command.

The :command:`run` sub-command does the following:

#. Execute the :ref:`nemo-prepare` via the :ref:`NEMO-CmdAPI` to set up a temporary run directory from which to execute the NEMO run.
#. Create a :file:`NEMO.sh` job script in the run directory.
   The job script:

   * runs NEMO
   * executes the :ref:`nemo-combine` to combine the per-processor restart and/or results files
   * executes the :ref:`nemo-deflate` to deflate the variables in the large netCDF results files using the Lempel-Ziv compression algorithm to reduce the size of the file on disk
   * executes the :ref:`nemo-gather` to collect the run description and results files into the results directory

#. Submit the job script to the queue manager via the command given by the :kbd:`--queue-job-cmd` option
   (which defaults to :command:`qsub`).

See the :ref:`RunDescriptionFileStructure` section for details of the run description YAML file.

The :command:`run` sub-command concludes by printing the path to the run directory and the response from the job queue manager.
Example:

.. code-block:: bash

    $ nemo run nemo.yaml $HOME/CANYONS/Mackenzie/myrun

    nemo_cmd.run INFO: nemo_cmd.prepare Created run directory ../../runs/38e87e0c-472d-11e3-9c8e-0025909a8461
    nemo_cmd.run INFO: 3330782.orca2.ibb

If the :command:`run` sub-command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.

If you are using on-the-fly deflation in :program:`XIOS-2`;
i.e. you are using 1 :program:`XIOS-2` process and have the :kbd:`compression_level="4"` attribute set in all of the :kbd:`file_group` definitions in your :file:`file_def.xml` file;
you should use the :kbd:`--no-deflate` option to exclude :ref:`nemo-deflate` from the :file:`NEMO.sh` job script.


.. _nemo-prepare:

:kbd:`prepare` Sub-command
==========================

The :command:`prepare` sub-command sets up a run directory from which to execute the NEMO run described in the specified run description,
and output file definitions files::

  usage: nemo prepare [-h] [--nocheck-initial-conditions] [-q] DESC_FILE

  Set up the NEMO run described in DESC_FILE and print the path to the run
  directory.

  positional arguments:
    DESC_FILE             run description YAML file

  optional arguments:
    -h, --help            show this help message and exit
    --nocheck-initial-conditions
                          Suppress checking of the initial conditions link.
                          Useful if you are submitting a job to an HPC qsub
                          queue and want the submitted job to wait for
                          completion of a previous job.
    -q, --quiet           don't show the run directory path on completion

See the :ref:`RunDescriptionFileStructure` section for details of the run description file.

The :command:`nemo prepare` command concludes by printing the path to the run directory it created.
Example:

.. code-block:: bash

    $ nemo prepare nemo.yaml

    nemo_cmd.prepare INFO: Created run directory ../../runs//38e87e0c-472d-11e3-9c8e-0025909a8461

The name of the run directory created is a `Universally Unique Identifier`_
(UUID)
string because the directory is intended to be ephemerally used for a single run.

.. _Universally Unique Identifier: https://en.wikipedia.org/wiki/Universally_unique_identifier

If the :command:`nemo prepare` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


Run Directory Contents
----------------------

The run directory contains:

* The run description file provided on the command line.

* A :file:`namelist_cfg`
  (the file name required by NEMO)
  file that is constructed by concatenating the namelist segments listed in the run description file
  (see :ref:`RunDescriptionFileStructure`).

* A symlink to the :file:`EXP00/namelist_ref` file in the directory of the NEMO configuration given by the :kbd:`config name` and :kbd:`NEMO code config` keys in the run description file is also created to provide default values to be used for any namelist variables not included in the namelist segments listed in the run description file.

* A symlink called :file:`bathy_meter.nc`
  (the file name required by NEMO)
  to the bathymetry file specified in the :kbd:`grid` section of the run description file.

* A symlink called :file:`coordinates.nc`
  (the file name required by NEMO)
  to the grid coordinates file specified in the :kbd:`grid` section of the run description file.

* A file called :file:`domain_def.xml`
  (the file name required by NEMO)
  that contains the XIOS output server domain definitions for the run.
  The file that is copied to :file:`domain_def.xml` is specified in the :kbd:`output` section of the run description file.

* A file called :file:`field_def.xml`
  (the file name required by NEMO)
  that contains the XIOS output server field definitions for the run.
  The file that is copied to :file:`field_def.xml` is specified in the :kbd:`output` section of the run description file.

* A file called :file:`iodefs.xml`
  (the file name required by NEMO).
  that file specifies the output files and variables they contain for the run.
  The file that is copied to :file:`iodefs.xml` is specified in the :kbd:`output` section of the run description file.
  It is also sometimes referred to as the NEMO IOM defs file.

* The :file:`nemo.exe` executable found in the :file:`BLD/bin/` directory of the NEMO configuration given by the :kbd:`config name` and :kbd:`NEMO code config` keys in the run description file.
  :command:`nemo prepare` aborts with an error message and exit code 2 if the :file:`nemo.exe` file is not found.
  In that case the run directory is not created.

* The :file:`xios_server.exe` executable found in the :file:`bin/` sub-directory of the directory given by the :kbd:`XIOS` key in the :kbd:`paths` section of the run description file.
  :command:`nemo prepare` aborts with an error message and exit code 2 if the :file:`xios_server.exe` file is not found.
  In that case the run directory is not created.

The run directory also contains symbolic links to forcing directories
(e.g. initial conditions,
atmospheric,
open boundary conditions,
rivers run-off,
etc.)
The names of those symlinks and the directories that they point to are given in the :kbd:`forcing` section of the run description file.
Please see :ref:`NEMO-3.6-Forcing` in the :ref:`RunDescriptionFileStructure` docs for full details.
It is your responsibility to ensure that these symlinks match the forcing directories given in your namelist files.

Finally,
if the run description YAML file contains a :kbd:`vcs revisions` section,
the run directory will contain 1 or more files whose names end with :file:`_rev.txt`.
The file names begin with the root directory names of the version control repositories given in the :kbd:`vcs revisions` section.
The files contain the output of the :command:`hg parents -v` command executed in the listed version control repositories.
Those files provide a record of the last committed revision of the repositories that will be in effect for the run,
which is important reproducibility information for the run.
If any of the listed repositories contain uncommitted changes,
the paths of the files and their status codes,
the output of the :command:`hg status -mardC` command,
will be appended to the repository's :file:`_rev.txt` file.
Please see the :ref:`NEMO-3.6-VCS-Revisions` for more details.


.. _nemo-combine:

:kbd:`combine` Sub-command
==========================

The :command:`combine` sub-command combines the per-processor results and/or restart files from an MPI NEMO run described in DESC_FILE using the the NEMO :command:`rebuild_nemo` tool::

  usage: nemo combine [-h] RUN_DESC_FILE

  Combine the per-processor results and/or restart files from an MPI NEMO run
  described in DESC_FILE using the the NEMO rebuild_nemo tool. Delete the per-
  processor files.

  positional arguments:
    RUN_DESC_FILE  file path/name of run description YAML file

  optional arguments:
    -h, --help     show this help message and exit

The per-processor files are deleted.

If the :command:`nemo combine` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


.. _nemo-deflate:

:kbd:`deflate` Sub-command
==========================

The :command:`deflate` sub-command deflates the variables in netCDF files using the Lempel-Ziv compression algorithm to reduce the size of the file on disk::

  usage: nemo deflate [-h] FILEPATH [FILEPATH ...]

  Deflate variables in netCDF files using Lempel-Ziv compression. Converts files
  to netCDF-4 format. The deflated file replaces the original file. This command
  is effectively the same as running ncks -4 -L -O FILEPATH FILEPATH for each FILEPATH.

  positional arguments:
    FILEPATH    Path/name of file to be deflated.

  optional arguments:
    -h, --help  show this help message and exit

You can give the command as many file names as you wish,
with or without paths.
You can also use shell wildcards and/or regular expressions to produce the list of file paths/names to deflate.

Storage savings can be as much as 80%.
Files processed by :command:`deflate` are converted to netCDF-4 format.
The deflated file replaces the original file,
but the deflation process uses temporary storage to prevent data loss.

:command:`nemo deflate` is equivalent to running:

.. code-block:: bash

    $ ncks -4 -L4 -O FILEPATH FILEPATH

on each :kbd:`FILEPATH`.

If the :command:`nemo deflate` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.


.. _nemo-gather:

:kbd:`gather` Sub-command
=========================

The :command:`gather` sub-command moves results from a NEMO run into a results directory::

  usage: nemo gather [-h] RESULTS_DIR

  Gather the results files from the NEMO run in the present working directory
  into files in RESULTS_DIR. The run description file, namelist(s), and other
  files that define the run are also gathered into RESULTS_DIR. If RESULTS_DIR
  does not exist it will be created.

  positional arguments:
    RESULTS_DIR  directory to store results into

  optional arguments:
    -h, --help   show this help message and exit

If the :command:`nemo gather` command prints an error message,
you can get a Python traceback containing more information about the error by re-running the command with the :kbd:`--debug` flag.
