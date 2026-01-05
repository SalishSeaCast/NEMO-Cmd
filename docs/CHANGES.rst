**********
Change Log
**********

v25.3 (unreleased)
==================

* Change to use Pixi_ to manage dependencies and operating environments.

  .. _Pixi: https://pixi.prefix.dev/latest/


v25.2 (2025-10-17)
==================

* Change to use Python 3.14 for package development.

* Add support for Python 3.14.

* Drop support for Python 3.11.
  The minimum supported Python version is now 3.12.


v25.1 (2025-10-17)
==================

* Not useful due to a release process error.


v24.2 (2024-12-30)
==================

* Improve release process documentation


v24.1 (2024-10-27)
==================

* Change to Python 3.13 for package development.


v23.1 (2023-11-20)
==================

* Change to Python 3.12 for package development.

* Drop support for Python 3.10.
  Minimum supported Python version is now 3.11.


v22.2 (2022-12-14)
==================

* Add :file:`envs/environment-hpc.yaml` to build conda environments on HPC clusters
  from which the package can be installed using the ``--user`` scheme for installation.

* Modernize packaging:

  * Replace :file:`setup.py` and :file:`setup.cfg` with :file:`pyproject.toml`
  * Change from ``setuptools`` to hatch_ for build backend

  .. _hatch: https://hatch.pypa.io/

* Add pre-commit to manage code style and repo QA.

* Change to use reusable GitHub Actions workflows from
  https://github.com/UBC-MOAD/gha-workflows.

* Change ``str.format()`` calls to f-string literals.

* Drop no longer needed unicode literal string markers.

* Change to Python 3.11 for package development.

* Drop support for Python 3.5, 3.6, 3.7, 3.8, and 3.9.
  Minimum supported Python version is now 3.10.
  Python 3.5 version deployed on ``orcinus`` is tagged ``orcinus-python-3.5``.


v22.1 (2022-05-02)
==================

* Move entry points from setup.py to setup.cfg.
  Supported by setuptools>=51.0.0 since 6-Dec-2020.

* Update example HPC module versions re: Compute Canada change to StdEnv/2020.


v21.1 (2021-10-21)
==================

* Change memory per node for ``sbatch`` runs to 0 to ensure that jobs go on to the "by-node"
  queue on ``graham``.
  The queue selection algorithm in the scheduler on ``graham`` appears to have changed
  (without announcement) on 13-Jul-2021 so that the previous memory per node of 125G
  now sends jobs to the "by-core" queue which is generally more crowded.

* Rename Git default branch from ``master`` to ``main``.

* Change continuous integration from Bitbucket pipeline to GitHub Actions workflow.
  CI reports are at https://github.com/SalishSeaCast/NEMO-Cmd/actions
  Unit test coverage report visualization is at https://app.codecov.io/gh/SalishSeaCast/NEMO-Cmd

* Migrate from Mercurial on Bitbucket to Git on GitHub due to Bitbucket's decision
  to terminate support for Mercurial.
  Repository is now at https://github.com/SalishSeaCast/NEMO-Cmd

* Expose ``nemo_cmd.prepare.record_vcs_revisions()`` function for use by packages like
  MOHID-Cmd that extend NEMO-Cmd.

* Enable version control system (VCS) revision recording for Git repositories:
  https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#vcs-revisions-section

* Replace ``namelist.py`` module with `f90nml`_ package.

  .. _f90nml: https://f90nml.readthedocs.io/en/latest/

* Change to new `MOAD package layout`_.

  .. _MOAD package layout: https://ubc-moad-docs.readthedocs.io/en/latest/python_packaging/pkg_structure.html


v19.1 (2019-08-26)
==================

* Add run description YAML file docs about ``land processor elimination`` option.

* Add Bitbucket continuous integration pipeline to run unit tests and generate unit
  tests coverage report.

* Drop support for Python 2.7; minimum version is now 3.5.

* Change to use `black`_ for code style management.

  .. _black: https://black.readthedocs.io/en/stable/

* Change to `CalVer`_ versioning convention.
  Version identifier format is now ``yy.n[.devn]``,
  where ``yy`` is the (post-2000) year of release,
  and ``n`` is the number of the release within the year, starting at ``1``.
  After a release has been made the value of ``n`` is incremented by 1,
  and ``.dev0`` is appended to the version identifier to indicate changes that will be
  included in the next release.
  ``v19.1.dev0`` is an exception to that scheme.
  That version identifies the period of development between the ``v1.3`` and ``v19.1``
  releases.

  .. _CalVer: https://calver.org/


1.3 (2019-01-20)
================

* Change to use ``python/3.7.0` module for `slurm workload manager`_ systems due to
  deprecation of ``python27-scipy-stack`` module on ``cedar.computecanada.ca`` and
  ``graham.computecanada.ca``.

* Add support for ``--waitjob`` command-line option on systems that use slurm resource
  manager.

* Expose functions in ``nemo_cmd.prepare`` for use by packages like SalishSeaCmd that
  extend NEMO-Cmd:

  * ``nemo_cmd.prepare.add_agrif_files()``
  * ``nemo_cmd.prepare.check_nemo_exec()``
  * ``nemo_cmd.prepare.check_xios_exec()``
  * ``nemo_cmd.prepare.copy_run_set_files()``
  * ``nemo_cmd.prepare.get_hg_revision()``
  * ``nemo_cmd.prepare.get_n_processors()``
  * ``nemo_cmd.prepare.load_run_desc()``
  * ``nemo_cmd.prepare.make_executable_links()``
  * ``nemo_cmd.prepare.make_forcing_links()``
  * ``nemo_cmd.prepare.make_grid_links()``
  * ``nemo_cmd.prepare.make_namelists()``
  * ``nemo_cmd.prepare.make_restart_links()``
  * ``nemo_cmd.prepare.make_run_dir()``
  * ``nemo_cmd.prepare.remove_run_dir()``
  * ``nemo_cmd.prepare.set_mpi_decomposition()``
  * ``nemo_cmd.prepare.write_repo_rev_file()``

* Fix bugs in the ``NEMO.sh`` script generation re: extra ``{}`` in some shell
  variable expressions.

* Drop support for NEMO-3.4.

* Fix a bug that caused ``prepare`` plug-in to fail for AGRIF runs that are
  not initialized from restart files.

* Add ``--no-deflate`` command-line option to exclude ``nemo-deflate`` from the
  ``NEMO.sh`` job script if you are using on-the-fly deflation in ``XIOS-2``;
  i.e. you are using 1 ``XIOS-2`` process and have the
  ``compression_level="4"`` attribute set in all of the ``file_group``
  definitions in your ``file_def.xml`` file.

* Change temporary run directory names from UUID to run id concatenated to
  microsecond resolution timestamp.

* Exclude ``cliff-2.9.0`` as a dependency due to `OpenStack bug #1719465`_.

  .. _OpenStack bug #1719465: https://bugs.launchpad.net/python-cliff/+bug/1719465


1.2 (2017-10-03)
================

* Add support for running on HPC systems that use the `slurm workload manager`_;
  e.g. ``cedar.computecanada.ca`` and ``graham.computecanada.ca``.

.. _slurm workload manager: https://slurm.schedmd.com/


1.1 (2017-09-30)
================

* Change from ``ncks`` to ``nccopy`` as tool underlying the ``deflate`` plug-in
  to reduce memory footprint.

* Add support for the use of `AGRIF`_ (Adaptive Grid Refinement in Fortran)
  in NEMO-3.6 runs.

.. _AGRIF: https://agrif.imag.fr/index.html

* Expand shell and user variables in namelist file paths.

* Use resolved repo path in VCS revisions recording message about uncommitted
  changes.

* Change to copy ref namelists to temporary run dir instead of symlinking them;
  facilitates easier run result archeology and reproducibility.

* Fix bug in atmospheric forcing file links checking function call.


1.0 (2017-04-27)
================

* Enable ``namelist.namelist2dict()`` to handle Fortran boolean values ``true``
  and ``false`` (no leading/trailing dots).

* Confirm that the ``rebuild_nemo.exe`` executable in the ``prepare`` plug-in
  so that a run is not executed without it only to fail when the ``combine``
  plug-in is run.
  See https://github.com/SalishSeaCast/NEMO-Cmd/issues/19.

* Add find_rebuild_nemo_script() to the API.
  See https://github.com/SalishSeaCast/NEMO-Cmd/issues/20.

* For NEMO-3.6 only,
  restart file paths/filenames are now specified in a new ``restart`` section
  instead of in the ``forcing`` section.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#restart-section.

* The existence of all paths/files given in the run description YAML file
  is confirmed.
  An informative error message is emitted for paths/files that don't exist.

* Add optional ``filedefs`` item to output section of run description YAML
  file to facilitate the use of a ``file_Def.xml`` file with XIOS-2.

* Change spelling of keys in output section of run description YAML file:

  * ``files`` becomes ``iodefs``
  *  ``domain`` becomes ``domaindefs``
  *  ``fields`` becomes ``fielddefs``

  Old spellings are retained as fall-backs for backward compatibility.

* Fix Python 2.7 Unicode/str issue in Mercurial version control revision
  and status recording.
  See https://github.com/SalishSeaCast/NEMO-Cmd/issues/16.

* Add option to provide in the run description YAML file a list of
  PBS resource key-value pairs to produce ``#PBS -l`` directives for in the
  run shell script.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#pbs-resources-section,
  and https://github.com/SalishSeaCast/NEMO-Cmd/issues/10.

* Add option to provide in the run description YAML file a list of
  HPC environment modules to include ``module load`` commands for in the
  run shell script.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#modules-to-load-section,
  and https://github.com/SalishSeaCast/NEMO-Cmd/issues/11.

* Add the option to use absolute paths for coordinates and bathymetry files
  in the run description YAML file.
  See https://nemo-cmd.readthedocs.io/en/latest/run_description_file/3.6_yaml_file.html#grid-section,
  and https://github.com/SalishSeaCast/NEMO-Cmd/issues/5.

* Add ``nemo_cmd.fspath()``,
  ``nemo_cmd.expanded_path()``,
  and ``nemo_cmd.resolved_path()`` functions for
  working with file system paths.
  See https://nemo-cmd.readthedocs.io/en/latest/api.html#functions-for-working-with-file-system-paths.

* Port in the SalishSeaCmd ``run`` plug-in in a minimal form sufficient for
  use on TORQUE/PBS systems that don't require special PBS feature (-l)
  directives,
  or loading of environment modules.

* Add optional recording of revision and status of Mercurial version control
  repositories via a new ``vcs revisions`` section in the run description YAML
  file.

* For NEMO-3.6 only,
  enable the use of ref namelists from directories other than from
  ``CONFIG/SHARED/``.
  The default is to symlink to ``CONFIG/SHARED/namelist*_ref`` when there are no
  ``namelist*_ref`` keys in the ``namelists`` section of the run description
  YAML file.

* Change from using pathlib to pathlib2 package for Python 2.7 because the
  latter is the backport from the Python 3 stdlib that is being kept up to date.

* Refactor the ``combine`` plug-in to only run ``rebuild_nemo`` to combine
  per-processor results and/or restart files.

* Add ``deflate`` plug-in to deflate variables in netCDF files using Lempel-Ziv
  compression.

* Fix a bug whereby results directories were gathered with a redundant directory
  layer;
  e.g. the files in ``runs/9e5958d4-cb95-11e6-a99b-00259059edac/restart/``
  were gathered to ``results/25dec16/restart/restart/`` instead of
  ``results/25dec16/restart/``.


0.9 (2016-12-30)
================

* Use `tox`_ for unified Python 2.7 and 3.5 testing.

  .. _tox: https://tox.wiki/en/latest/

* Refactor the ``gather`` plug-in in a minimal form sufficient for use by the
  ``GoMSS_Nowcast`` package.

* Refactor the ``prepare`` plug-in as the first ``nemo`` subcommand.

* Add token-based Fortran namelist parser from gist.github.com/krischer/4943658.
  That module also exists in the ``tools/SalishSeaTools`` package.
  It was brought into this package to avoid making this package depend on
  ``SalishSeaTools``.

* Adopt yapf for code style management.
  Project-specific style rules are set in ``.style.yapf``.

* Initialize project from the SalishSeaCmd/ directory of the tools repo with::

    hg convert --filemap tools/NEMO-Cmd_filemap.txt tools NEMO-Cmd

  A copy of ``NEMO-Cmd_filemap.txt`` is included in this repo.
