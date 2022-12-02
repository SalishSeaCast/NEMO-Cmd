# Copyright 2013 – present by the SalishSeaCast contributors
# and The University of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# SPDX-License-Identifier: Apache-2.0


"""NEMO-Cmd command plug-in for prepare sub-command.

Sets up the necessary symbolic links for a NEMO run
in a specified directory and changes the pwd to that directory.
"""
from copy import copy, deepcopy
import functools
import logging
import os
from pathlib import Path
import shutil
import tempfile
import time
import xml.etree.ElementTree

import arrow
import cliff.command
from dateutil import tz
import f90nml
import git
import hglib
import yaml

from nemo_cmd import fspath, resolved_path, expanded_path
from nemo_cmd.combine import find_rebuild_nemo_script

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Prepare(cliff.command.Command):
    """Prepare a NEMO run"""

    def get_parser(self, prog_name):
        parser = super(Prepare, self).get_parser(prog_name)
        parser.description = """
            Set up the NEMO run described in DESC_FILE
            and print the path to the run directory.
        """
        parser.add_argument(
            "desc_file",
            metavar="DESC_FILE",
            type=Path,
            help="run description YAML file",
        )
        parser.add_argument(
            "--nocheck-initial-conditions",
            dest="nocheck_init",
            action="store_true",
            help="""
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to an HPC qsub queue and want
            the submitted job to wait for completion of a previous job.
            """,
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="don't show the run directory path on completion",
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `nemo prepare` sub-command.

        A UUID named directory is created and symbolic links are created
        in the directory to the files and directories specified to run NEMO.
        The path to the run directory is logged to the console on completion
        of the set-up.
        """
        run_dir = prepare(parsed_args.desc_file, parsed_args.nocheck_init)
        if not parsed_args.quiet:
            logger.info(f"Created run directory {run_dir}")
        return run_dir


def prepare(desc_file, nocheck_init):
    """Create and prepare the temporary run directory.

    The temporary run directory is created with a UUID as its name.
    Symbolic links are created in the directory to the files and
    directories specified to run NEMO.
    The path to the run directory is returned.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress initial condition link check;
                                 the default is to check

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_desc = load_run_desc(desc_file)
    nemo_bin_dir = check_nemo_exec(run_desc)
    xios_bin_dir = check_xios_exec(run_desc)
    find_rebuild_nemo_script(run_desc)
    run_set_dir = resolved_path(desc_file).parent
    run_dir = make_run_dir(run_desc)
    make_namelists(run_set_dir, run_desc, run_dir)
    copy_run_set_files(run_desc, desc_file, run_set_dir, run_dir)
    make_executable_links(nemo_bin_dir, run_dir, xios_bin_dir)
    make_grid_links(run_desc, run_dir)
    make_forcing_links(run_desc, run_dir)
    make_restart_links(run_desc, run_dir, nocheck_init)
    record_vcs_revisions(run_desc, run_dir)
    add_agrif_files(run_desc, desc_file, run_set_dir, run_dir, nocheck_init)
    return run_dir


def load_run_desc(desc_file):
    """Load the run description file contents into a data structure.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :returns: Contents of run description file parsed from YAML into a dict.
    :rtype: dict
    """
    with open(fspath(desc_file), "rt") as f:
        run_desc = yaml.safe_load(f)
    return run_desc


def get_run_desc_value(
    run_desc, keys, expand_path=False, resolve_path=False, run_dir=None, fatal=True
):
    """Get the run description value defined by the sequence of keys.

    :param dict run_desc: Run description dictionary.

    :param sequence keys: Keys that lead to the value to be returned.

    :param boolean expand_path: When :py:obj:`True`, return the value as a
                                :class:`pathlib.Path` object with shell and
                                user variables expanded via
                                :func:`nemo_cmd.expanded_path`.

    :param boolean resolve_path: When :py:obj:`True`, return the value as an
                                 absolute :class:`pathlib.Path` object with
                                 shell and user variables expanded and symbolic
                                 links resolved via
                                 :func:`nemo_cmd.resolved_path`.
                                 Also confirm that the path exists,
                                 otherwise,
                                 raise a :py:exc:`SystemExit` exception.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean fatal: When :py:obj:`True`, delete the under construction
                          temporary run directory, and raise a
                          :py:exc:`SystemExit` exception.
                          Otherwise, raise a :py:exc:`KeyError` exception.

    :raises: :py:exc:`SystemExit` or :py:exc:`KeyError`

    :returns: Run description value defined by the sequence of keys.
    """
    try:
        value = run_desc
        for key in keys:
            value = value[key]
    except KeyError:
        if not fatal:
            raise
        logger.error(
            f'"{": ".join(keys)}" key not found - please check your run description YAML file'
        )
        if run_dir:
            remove_run_dir(run_dir)
        raise SystemExit(2)
    if expand_path:
        value = expanded_path(value)
    if resolve_path:
        value = resolved_path(value)
        if not value.exists():
            logger.error(
                f'{value} path from "{": ".join(keys)}" key not found - please check your '
                f"run description YAML file"
            )
            if run_dir:
                remove_run_dir(run_dir)
            raise SystemExit(2)
    return value


def check_nemo_exec(run_desc):
    """Calculate absolute path of the NEMO executable's directory.

    Confirm that the NEMO executable exists, raising a SystemExit
    exception if it does not.

    :param dict run_desc: Run description dictionary.

    :returns: Absolute path of NEMO executable's directory.
    :rtype: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    try:
        nemo_config_dir = get_run_desc_value(
            run_desc, ("paths", "NEMO code config"), resolve_path=True, fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        nemo_config_dir = get_run_desc_value(
            run_desc, ("paths", "NEMO-code-config"), resolve_path=True
        )
    try:
        config_name = get_run_desc_value(run_desc, ("config name",), fatal=False)
    except KeyError:
        # Alternate key spelling for backward compatibility
        config_name = get_run_desc_value(run_desc, ("config_name",))
    nemo_bin_dir = nemo_config_dir / config_name / "BLD" / "bin"
    nemo_exec = nemo_bin_dir / "nemo.exe"
    if not nemo_exec.exists():
        logger.error(f"{nemo_exec} not found - did you forget to build it?")
        raise SystemExit(2)
    return nemo_bin_dir


def check_xios_exec(run_desc):
    """Calculate absolute path of the XIOS executable's directory.

    Confirm that the XIOS executable exists, raising a SystemExit
    exception if it does not.

    :param dict run_desc: Run description dictionary.

    :returns: Absolute path of XIOS executable's directory.
    :rtype: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    xios_code_path = get_run_desc_value(run_desc, ("paths", "XIOS"), resolve_path=True)
    xios_bin_dir = xios_code_path / "bin"
    xios_exec = xios_bin_dir / "xios_server.exe"
    if not xios_exec.exists():
        logger.error(f"{xios_exec} not found - did you forget to build it?")
        raise SystemExit(2)
    return xios_bin_dir


def make_run_dir(run_desc):
    """Create the temporary directory from which NEMO will be run.

    The location is in the runs directory from the run description,
    and its name is the run id combined with an ISO-format date/time stamp.

    :param dict run_desc: Run description dictionary.

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_id = get_run_desc_value(run_desc, ("run_id",))
    runs_dir = get_run_desc_value(
        run_desc, ("paths", "runs directory"), resolve_path=True
    )
    run_dir = runs_dir / f"{run_id}_{arrow.now().format('YYYY-MM-DDTHHmmss.SSSSSSZ')}"
    run_dir.mkdir()
    return run_dir


def remove_run_dir(run_dir):
    """Remove all files from run_dir, then remove run_dir.

    Intended to be used as a clean-up operation when some other part
    of the prepare process fails.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    """
    # Allow time for the OS to flush file buffers to disk
    time.sleep(0.1)
    try:
        for p in run_dir.iterdir():
            p.unlink()
        run_dir.rmdir()
    except OSError:
        pass


def make_namelists(run_set_dir, run_desc, run_dir, agrif_n=None):
    """Build the namelist files for the NEMO run in run_dir by
    concatenating the lists of namelist section files provided in run_desc.

    If any of the required namelist section files are missing,
    delete the run directory and raise a :py:exc:`SystemExit` exception.

    :param run_set_dir: Directory containing the run description file,
                        from which relative paths for the namelist section
                        files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    try:
        nemo_config_dir = get_run_desc_value(
            run_desc,
            ("paths", "NEMO code config"),
            resolve_path=True,
            run_dir=run_dir,
            fatal=False,
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        nemo_config_dir = get_run_desc_value(
            run_desc, ("paths", "NEMO-code-config"), resolve_path=True, run_dir=run_dir
        )
    try:
        config_name = get_run_desc_value(
            run_desc, ("config name",), run_dir=run_dir, fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        config_name = get_run_desc_value(run_desc, ("config_name",), run_dir=run_dir)
    keys = ("namelists",)
    if agrif_n is not None:
        keys = ("namelists", f"AGRIF_{agrif_n}")
    namelists = get_run_desc_value(run_desc, keys, run_dir=run_dir)
    for namelist_filename in namelists:
        if namelist_filename.startswith("AGRIF"):
            continue
        namelist_dest = namelist_filename
        keys = ("namelists", namelist_filename)
        if agrif_n is not None:
            namelist_dest = f"{agrif_n}_{namelist_filename}"
            keys = (
                f"namelists",
                f"AGRIF_{agrif_n}",
                namelist_filename,
            )
        with (run_dir / namelist_dest).open("wt") as namelist:
            namelist_files = get_run_desc_value(run_desc, keys, run_dir=run_dir)
            for nl in namelist_files:
                nl_path = expanded_path(nl)
                if not nl_path.is_absolute():
                    nl_path = run_set_dir / nl_path
                try:
                    with nl_path.open("rt") as f:
                        namelist.writelines(f.readlines())
                        namelist.write("\n\n")
                except IOError as e:
                    logger.error(e)
                    namelist.close()
                    remove_run_dir(run_dir)
                    raise SystemExit(2)
        ref_namelist = namelist_filename.replace("_cfg", "_ref")
        if ref_namelist not in namelists:
            ref_namelist_source = nemo_config_dir / config_name / "EXP00" / ref_namelist
            shutil.copy2(
                fspath(ref_namelist_source),
                fspath(run_dir / namelist_dest.replace("_cfg", "_ref")),
            )
    if "namelist_cfg" in namelists:
        set_mpi_decomposition("namelist_cfg", run_desc, run_dir)
    else:
        logger.error(
            "No namelist_cfg key found in namelists section of run description"
        )
        remove_run_dir(run_dir)
        raise SystemExit(2)


def set_mpi_decomposition(namelist_filename, run_desc, run_dir):
    """Update the &nammpp namelist jpni & jpnj values with the MPI
    decomposition values from the run description.

    A :py:exc:`SystemExit` exception is raise if there is no MPI decomposition
    specified in the run description.

    :param str namelist_filename: The name of the namelist file.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    try:
        jpni, jpnj = map(
            int,
            get_run_desc_value(run_desc, ("MPI decomposition",), fatal=False).split(
                "x"
            ),
        )
    except KeyError:
        logger.error(
            "MPI decomposition value not found in YAML run description file. "
            "Please add a line like:\n"
            "  MPI decomposition: 8x18\n"
            "that says how you want the domain distributed over the "
            "processors in the i (longitude) and j (latitude) dimensions."
        )
        remove_run_dir(run_dir)
        raise SystemExit(2)
    patch = {
        "nammpp": {
            "jpni": jpni,
            "jpnj": jpnj,
            "jpnij": get_n_processors(run_desc, run_dir),
        }
    }
    _patch_namelist(run_dir / namelist_filename, patch)


def _patch_namelist(namelist_path, patch):
    """
    :param :py:class:`pathlib.Path` namelist_path:
    :param dict patch:
    """
    # f90nml insists on writing the patched namelist to a file,
    # so we use a temporary file and copy it on to the original namelist file
    with tempfile.NamedTemporaryFile("wt", delete=False) as tmp_patched_namelist:
        f90nml.patch(fspath(namelist_path), patch, tmp_patched_namelist)
    mode_b4_copy = namelist_path.stat().st_mode
    shutil.copy2(tmp_patched_namelist.name, fspath(namelist_path))
    namelist_path.chmod(mode_b4_copy)
    Path(tmp_patched_namelist.name).unlink()


def get_n_processors(run_desc, run_dir):
    """Return the total number of processors required for the run as
    specified by the MPI decomposition key in the run description.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Number of processors required for the run.
    :rtype: int
    """
    jpni, jpnj = map(
        int, get_run_desc_value(run_desc, ("MPI decomposition",)).split("x")
    )
    try:
        mpi_lpe_mapping = get_run_desc_value(
            run_desc, ("grid", "land processor elimination"), fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        try:
            mpi_lpe_mapping = get_run_desc_value(
                run_desc, ("grid", "Land processor elimination"), fatal=False
            )
        except KeyError:
            logger.warning(
                "No grid: land processor elimination: key found in run "
                "description YAML file, so proceeding on the assumption that "
                "you want to run without land processor elimination"
            )
            mpi_lpe_mapping = False
    if not mpi_lpe_mapping:
        return jpni * jpnj

    try:
        mpi_lpe_mapping = get_run_desc_value(
            run_desc,
            ("grid", "land processor elimination"),
            expand_path=True,
            fatal=False,
            run_dir=run_dir,
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        mpi_lpe_mapping = get_run_desc_value(
            run_desc,
            ("grid", "Land processor elimination"),
            expand_path=True,
            run_dir=run_dir,
        )
    if not mpi_lpe_mapping.is_absolute():
        nemo_forcing_dir = get_run_desc_value(
            run_desc, ("paths", "forcing"), resolve_path=True, run_dir=run_dir
        )
        mpi_lpe_mapping = nemo_forcing_dir / "grid" / mpi_lpe_mapping
    n_processors = _lookup_lpe_n_processors(mpi_lpe_mapping, jpni, jpnj)
    if n_processors is None:
        msg = f"No land processor elimination choice found for {jpni}x{jpnj} MPI decomposition"
        logger.error(msg)
        raise ValueError(msg)
    return n_processors


def _lookup_lpe_n_processors(mpi_lpe_mapping, jpni, jpnj):
    """Encapsulate file access to facilitate testability of get_n_processors()."""
    with mpi_lpe_mapping.open("rt") as f:
        for line in f:
            cjpni, cjpnj, cnw = map(int, line.split(","))
            if jpni == cjpni and jpnj == cjpnj:
                return cnw


def copy_run_set_files(run_desc, desc_file, run_set_dir, run_dir, agrif_n=None):
    """Copy the run-set files given into run_dir.

    The YAML run description file (from the command-line) is copied.
    The IO defs file is also copied.
    The file path/name of the IO defs file is taken from the :kbd:`output`
    stanza of the YAML run description file.
    The IO defs file is copied as :file:`iodef.xml` because that is the
    name that XIOS expects.

    The domain defs and field defs files used by XIOS are also copied.
    Those file paths/names of those file are taken from the :kbd:`output`
    stanza of the YAML run description file.
    They are copied to :file:`domain_def.xml` and :file:`field_def.xml`,
    respectively, because those are the file names that XIOS expects.
    Optionally, the file defs file used by XIOS-2 is also copied.
    Its file path/name is also taken from the :kbd:`output` stanza.
    It is copied to :file:`file_def.xml` because that is the file name that
    XIOS-2 expects.

    :param dict run_desc: Run description dictionary.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param run_set_dir: Directory containing the run description file,
                        from which relative paths for the namelist section
                        files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.
    """
    try:
        iodefs = get_run_desc_value(
            run_desc,
            ("output", "iodefs"),
            resolve_path=True,
            run_dir=run_dir,
            fatal=False,
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        iodefs = get_run_desc_value(
            run_desc, ("output", "files"), resolve_path=True, run_dir=run_dir
        )
    run_set_files = [
        (iodefs, "iodef.xml"),
        (run_set_dir / desc_file.name, desc_file.name),
    ]
    try:
        keys = ("output", "domaindefs")
        domain_def_filename = "domain_def.xml"
        if agrif_n is not None:
            keys = ("output", f"AGRIF_{agrif_n}", "domaindefs")
            domain_def_filename = f"{agrif_n}_domain_def.xml"
        domains_def = get_run_desc_value(
            run_desc, keys, resolve_path=True, run_dir=run_dir, fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        keys = ("output", "domain")
        if agrif_n is not None:
            keys = ("output", f"AGRIF_{agrif_n}", "domain")
        domains_def = get_run_desc_value(
            run_desc, keys, resolve_path=True, run_dir=run_dir
        )
    try:
        fields_def = get_run_desc_value(
            run_desc,
            ("output", "fielddefs"),
            resolve_path=True,
            run_dir=run_dir,
            fatal=False,
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        fields_def = get_run_desc_value(
            run_desc, ("output", "fields"), resolve_path=True, run_dir=run_dir
        )
    run_set_files.extend(
        [(domains_def, domain_def_filename), (fields_def, "field_def.xml")]
    )
    try:
        keys = ("output", "filedefs")
        file_def_filename = "file_def.xml"
        if agrif_n is not None:
            keys = ("output", f"AGRIF_{agrif_n}", "filedefs")
            file_def_filename = f"{agrif_n}_file_def.xml"
        files_def = get_run_desc_value(
            run_desc, keys, resolve_path=True, run_dir=run_dir, fatal=False
        )
        run_set_files.append((files_def, file_def_filename))
    except KeyError:
        # `files` key is optional and only used with XIOS-2
        pass
    for source, dest_name in run_set_files:
        shutil.copy2(fspath(source), fspath(run_dir / dest_name))
    _set_xios_server_mode(run_desc, run_dir)


def _set_xios_server_mode(run_desc, run_dir):
    """Update the :file:`iodef.xml` :kbd:`xios` context :kbd:`using_server`
    variable text with the :kbd:`separate XIOS server` value from the
    run description.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    try:
        sep_xios_server = get_run_desc_value(
            run_desc, ("output", "separate XIOS server"), fatal=False
        )
    except KeyError:
        logger.error(
            "separate XIOS server key/value not found in output section "
            "of YAML run description file. "
            "Please add lines like:\n"
            "  separate XIOS server: True\n"
            "  XIOS servers: 1\n"
            "that say whether to run the XIOS server(s) attached or detached, "
            "and how many of them to use."
        )
        remove_run_dir(run_dir)
        raise SystemExit(2)
    tree = xml.etree.ElementTree.parse(fspath(run_dir / "iodef.xml"))
    root = tree.getroot()
    using_server = root.find('context[@id="xios"]//variable[@id="using_server"]')
    using_server.text = "true" if sep_xios_server else "false"
    using_server_line = xml.etree.ElementTree.tostring(using_server).decode()
    with (run_dir / "iodef.xml").open("rt") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "using_server" in line:
            lines[i] = using_server_line
            break
    with (run_dir / "iodef.xml").open("wt") as f:
        f.writelines(lines)


def make_executable_links(nemo_bin_dir, run_dir, xios_bin_dir):
    """Create symlinks in run_dir to the NEMO and XIOS executables.

    :param nemo_bin_dir: Absolute path of directory containing NEMO executable.
    :type nemo_bin_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param xios_bin_dir: Absolute path of directory containing XIOS executable.
    :type xios_bin_dir: :py:class:`pathlib.Path`
    """
    nemo_exec = nemo_bin_dir / "nemo.exe"
    (run_dir / "nemo.exe").symlink_to(nemo_exec)
    xios_server_exec = xios_bin_dir / "xios_server.exe"
    (run_dir / "xios_server.exe").symlink_to(xios_server_exec)


def make_grid_links(run_desc, run_dir, agrif_n=None):
    """Create symlinks in run_dir to the file names that NEMO expects
    to the bathymetry and coordinates files given in the run_desc dict.

    For AGRIF sub-grids, the symlink names are prefixed with the agrif_n;
    e.g. 1_coordinates.nc.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.

    :raises: :py:exc:`SystemExit` with exit code 2
    """
    coords_keys = ("grid", "coordinates")
    coords_filename = "coordinates.nc"
    bathy_keys = ("grid", "bathymetry")
    bathy_filename = "bathy_meter.nc"
    if agrif_n is not None:
        coords_keys = ("grid", f"AGRIF_{agrif_n}", "coordinates")
        coords_filename = f"{agrif_n}_coordinates.nc"
        bathy_keys = ("grid", f"AGRIF_{agrif_n}", "bathymetry")
        bathy_filename = f"{agrif_n}_bathy_meter.nc"
    coords_path = get_run_desc_value(
        run_desc, coords_keys, expand_path=True, run_dir=run_dir
    )
    bathy_path = get_run_desc_value(
        run_desc, bathy_keys, expand_path=True, run_dir=run_dir
    )
    if coords_path.is_absolute() and bathy_path.is_absolute():
        grid_paths = ((coords_path, coords_filename), (bathy_path, bathy_filename))
    else:
        nemo_forcing_dir = get_run_desc_value(
            run_desc, ("paths", "forcing"), resolve_path=True, run_dir=run_dir
        )
        grid_dir = nemo_forcing_dir / "grid"
        grid_paths = (
            (grid_dir / coords_path, coords_filename),
            (grid_dir / bathy_path, bathy_filename),
        )
    for source, link_name in grid_paths:
        if not source.exists():
            logger.error(
                f"{source} not found; cannot create symlink - "
                f"please check the forcing path and grid file names in your run description file"
            )
            remove_run_dir(run_dir)
            raise SystemExit(2)
        (run_dir / link_name).symlink_to(source)


def make_forcing_links(run_desc, run_dir):
    """Create symlinks in run_dir to the forcing directory/file names given
    in the run description forcing section.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2 if a symlink target
             does not exist
    """
    link_checkers = {"atmospheric": _check_atmospheric_forcing_link}
    link_names = get_run_desc_value(run_desc, ("forcing",), run_dir=run_dir)
    for link_name in link_names:
        source = _resolve_forcing_path(run_desc, (link_name, "link to"), run_dir)
        if not source.exists():
            logger.error(
                f"{source} not found; cannot create symlink - "
                f"please check the forcing paths and file names in your run description file"
            )
            remove_run_dir(run_dir)
            raise SystemExit(2)
        (run_dir / link_name).symlink_to(source)
        try:
            link_checker = get_run_desc_value(
                run_desc,
                ("forcing", link_name, "check link"),
                run_dir=run_dir,
                fatal=False,
            )
            link_checkers[link_checker["type"]](
                run_dir, source, link_checker["namelist filename"]
            )
        except KeyError:
            if "check link" not in link_names[link_name]:
                # No forcing link checker specified
                pass
            else:
                if link_checker is not None:
                    logger.error(f"unknown forcing link checker: {link_checker}")
                    remove_run_dir(run_dir)
                    raise SystemExit(2)


def _resolve_forcing_path(run_desc, keys, run_dir):
    """Calculate a resolved path for a forcing path.

    If the path in the run description is absolute, resolve any symbolic links,
    etc. in it.

    If the path is relative, append it to the NEMO-forcing repo path from the
    run description.

    :param dict run_desc: Run description dictionary.

    :param tuple keys: Key sequence in the :kbd:`forcing` section of the
                       run description for which the resolved path calculated.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :return: Resolved path
    :rtype: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` with exit code 2 if the NEMO-forcing repo
             path does not exist
    """
    path = get_run_desc_value(
        run_desc, (("forcing",) + keys), expand_path=True, fatal=False
    )
    if path.is_absolute():
        return path.resolve()
    nemo_forcing_dir = get_run_desc_value(
        run_desc, ("paths", "forcing"), resolve_path=True, run_dir=run_dir
    )
    return nemo_forcing_dir / path


def _check_atmospheric_forcing_link(run_dir, link_path, namelist_filename):
    """Confirm that the atmospheric forcing files necessary for the NEMO
    run are present.

    Sections of the namelist file are parsed to determine
    the necessary files, and the date ranges required for the run.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param link_path: Path of the atmospheric forcing files collection.
    :type :py:class:`pathlib.Path`:

    :param str namelist_filename: File name of the namelist to parse for
                                  atmospheric file names and date ranges.

    :raises: :py:exc:`SystemExit` with exit code 2 if an atmospheric forcing
             file does not exist
    """
    namelist = f90nml.read(fspath(run_dir / namelist_filename))
    if not namelist["namsbc"]["ln_blk_core"]:
        return
    start_date = arrow.get(str(namelist["namrun"]["nn_date0"]), "YYYYMMDD")
    it000 = namelist["namrun"]["nn_it000"]
    itend = namelist["namrun"]["nn_itend"]
    dt = namelist["namdom"]["rn_rdt"]
    end_date = start_date.replace(seconds=(itend - it000) * dt - 1)
    qtys = "sn_wndi sn_wndj sn_qsr sn_qlw sn_tair sn_humi sn_prec sn_snow".split()
    core_dir = namelist["namsbc_core"]["cn_dir"]
    file_info = {"core": {"dir": core_dir, "params": []}}
    for qty in qtys:
        flread_params = namelist["namsbc_core"][qty]
        file_info["core"]["params"].append((flread_params[0], flread_params[5]))
    if namelist["namsbc"]["ln_apr_dyn"]:
        apr_dir = namelist["namsbc_apr"]["cn_dir"]
        file_info["apr"] = {"dir": apr_dir, "params": []}
        flread_params = namelist["namsbc_apr"]["sn_apr"]
        file_info["apr"]["params"].append((flread_params[0], flread_params[5]))
    startm1 = start_date.replace(days=-1)
    for r in arrow.Arrow.range("day", startm1, end_date):
        for v in file_info.values():
            for basename, period in v["params"]:
                if period == "daily":
                    file_path = os.path.join(
                        v["dir"],
                        f"{basename}_y{r.year}m{r.month:02d}d{r.day:02d}.nc",
                    )
                elif period == "yearly":
                    file_path = os.path.join(v["dir"], f"{basename}.nc")
                if not (run_dir / file_path).exists():
                    logger.error(
                        f"{file_path} not found; please confirm that atmospheric forcing "
                        f"files for {startm1.format('YYYY-MM-DD')} through "
                        f"{end_date.format('YYYY-MM-DD')} are in the {link_path} collection, "
                        f"and that atmospheric forcing paths in your run description and "
                        f"surface boundary conditions namelist are in agreement."
                    )
                    remove_run_dir(run_dir)
                    raise SystemExit(2)


def make_restart_links(run_desc, run_dir, nocheck_init, agrif_n=None):
    """Create symlinks in run_dir to the restart files given in the
    run description restart section.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress restart file existence check;
                                 the default is to check

    :param int agrif_n: AGRIF sub-grid number.

    :raises: :py:exc:`SystemExit` with exit code 2 if a symlink target does
             not exist
    """
    keys = ("restart",)
    if agrif_n is not None:
        keys = ("restart", f"AGRIF_{agrif_n}")
    try:
        link_names = get_run_desc_value(run_desc, keys, run_dir=run_dir, fatal=False)
    except KeyError:
        logger.warning(
            "No restart section found in run description YAML file, "
            "so proceeding on the assumption that initial conditions "
            "have been provided"
        )
        return
    for link_name in link_names:
        if link_name.startswith("AGRIF"):
            continue
        keys = ("restart", link_name)
        if agrif_n is not None:
            keys = ("restart", f"AGRIF_{agrif_n}", link_name)
            link_name = f"{agrif_n}_{link_name}"
        source = get_run_desc_value(run_desc, keys, expand_path=True)
        if not source.exists() and not nocheck_init:
            logger.error(
                f"{source} not found; cannot create symlink - "
                f"please check the restart file paths and file names in your run description file"
            )
            remove_run_dir(run_dir)
            raise SystemExit(2)
        if nocheck_init:
            (run_dir / link_name).symlink_to(source)
        else:
            (run_dir / link_name).symlink_to(source.resolve())


def record_vcs_revisions(run_desc, run_dir):
    """Record revision and status information from version control system
    repositories in files in the temporary run directory.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    """
    if "vcs revisions" not in run_desc:
        return
    vcs_funcs = {"git": get_git_revision, "hg": get_hg_revision}
    vcs_tools = get_run_desc_value(run_desc, ("vcs revisions",), run_dir=run_dir)
    for vcs_tool in vcs_tools:
        repos = get_run_desc_value(
            run_desc, ("vcs revisions", vcs_tool), run_dir=run_dir
        )
        for repo in repos:
            write_repo_rev_file(Path(repo), run_dir, vcs_funcs[vcs_tool])


def write_repo_rev_file(repo, run_dir, vcs_func):
    """Write revision and status information from a version control
    system repository to a file in the temporary run directory.

    The file name is the repository directory name with :kbd:`_rev.txt`
    appended.

    :param repo: Path of Mercurial repository to get revision and status
                 information from.
    :type repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param vcs_func: Function to call to gather revision and status
                     information from repo.
    """
    repo_path = resolved_path(repo)
    repo_rev_file_lines = vcs_func(repo_path, run_dir)
    if repo_rev_file_lines:
        rev_file = run_dir / f"{repo_path.name}_rev.txt"
        with rev_file.open("wt") as f:
            f.writelines(f"{line}\n" for line in repo_rev_file_lines)


def get_git_revision(git_repo, run_dir):
    """Gather revision and status information from a Git repo.

    Effectively record the output of :command:`git branch --show-current`,
    :command:`git log -1`, :command:`git show --pretty="" --name-only`,
    and :command:`git diff --name-status`.

    Files named :file:`CONFIG/cfg.txt` and
    :file:`TOOLS/COMPILE/full_key_list.txt` are ignored because they change
    frequently but the changes generally of no consequence;
    see https://github.com/SalishSea/CastNEMO-Cmd/issues/18.

    :param git_repo: Path of Git repository to get revision and status information from.
    :type git_repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Git repository revision and status information strings.
    :rtype: list
    """
    if not git_repo.exists():
        logger.warning(
            f"revision and status requested for non-existent repo: {git_repo}"
        )
        return []
    repo_path = copy(git_repo)
    while fspath(git_repo) != repo_path.root:
        try:
            repo = git.Repo(fspath(git_repo))
            break
        except git.exc.InvalidGitRepositoryError:
            git_repo = git_repo.parent
    else:
        logger.error(f"unable to find Git repo root in or above {repo_path}")
        remove_run_dir(run_dir)
        raise SystemExit(2)
    branch = repo.active_branch
    commit = repo.commit(branch)
    author_datetime = arrow.get(commit.authored_datetime)
    repo_rev_file_lines = [
        f"branch: {branch}",
        f"commit: {commit.hexsha}",
    ]
    if repo.tags:
        for tag in repo.tags:
            if commit.hexsha == tag.commit:
                repo_rev_file_lines.append(f"tag:    {tag.name}")
    repo_rev_file_lines.extend(
        [
            f"author: {commit.author}",
            f"date:   {author_datetime.format('ddd MMM DD HH:mm:ss YYYY ZZ')}",
            f"files:  {' '.join(d.a_path for d in commit.diff('HEAD~1'))}",
            f"message:",
            f"{commit.message}",
        ]
    )
    if commit.diff(None):
        ignore = ("CONFIG/cfg.txt", "TOOLS/COMPILE/full_key_list.txt")
        diffs = deepcopy(commit.diff(None))
        for d in deepcopy(diffs):
            if d.a_path.endswith(ignore):
                diffs.remove(d)
        if diffs:
            logger.warning(f"There are uncommitted changes in {repo_path}")
            repo_rev_file_lines.append("uncommitted changes:")
            repo_rev_file_lines.extend(f"{d.change_type} {d.a_path}" for d in diffs)
    return repo_rev_file_lines


def get_hg_revision(hg_repo, run_dir):
    """Gather revision and status information from a Mercurial repo.

    Effectively record the output of :command:`hg parents -v` and
    :command:`hg status -mardC`.

    Files named :file:`CONFIG/cfg.txt` and
    :file:`TOOLS/COMPILE/full_key_list.txt` are ignored because they change
    frequently but the changes generally of no consequence;
    see https://github.com/SalishSeaCast/NEMO-Cmd/issues/18.

    :param hg_repo: Path of Mercurial repository to get revision and status
                    information from.
    :type hg_repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Mercurial repository revision and status information strings.
    :rtype: list
    """
    if not hg_repo.exists():
        logger.warning(
            f"revision and status requested for non-existent repo: {hg_repo}"
        )
        return []
    repo_path = copy(hg_repo)
    while fspath(hg_repo) != repo_path.root:
        try:
            with hglib.open(fspath(hg_repo)) as hg:
                parents = hg.parents()
                files = [f[1] for f in hg.status(change=[parents[0].rev])]
                status = hg.status(
                    modified=True, added=True, removed=True, deleted=True, copies=True
                )
            break
        except hglib.error.ServerError:
            hg_repo = hg_repo.parent
    else:
        logger.error(f"unable to find Mercurial repo root in or above {repo_path}")
        remove_run_dir(run_dir)
        raise SystemExit(2)
    revision = parents[0]
    repo_rev_file_lines = [
        f"changset:   {revision.rev.decode()}:{revision.node.decode()}"
    ]
    if revision.tags:
        repo_rev_file_lines.append(f"tag:        {revision.tags.decode()}")
    if len(parents) > 1:
        repo_rev_file_lines.extend(
            f"parent:     {parent.rev.decode()}:{parent.node.decode()}"
            for parent in parents
        )
    date = arrow.get(revision.date).replace(tzinfo=tz.tzlocal())
    repo_rev_file_lines.extend(
        [
            f"user:       {revision.author.decode()}",
            f"date:       {date.format('ddd MMM DD HH:mm:ss YYYY ZZ')}",
            f"files:      {' '.join(f.decode() for f in files)}",
            f"description:",
        ]
    )
    repo_rev_file_lines.extend(line.decode() for line in revision.desc.splitlines())
    ignore = ("CONFIG/cfg.txt", "TOOLS/COMPILE/full_key_list.txt")
    for s in copy(status):
        if s[1].decode().endswith(ignore):
            status.remove(s)
    if status:
        logger.warning(f"There are uncommitted changes in {repo_path}")
        repo_rev_file_lines.append("uncommitted changes:")
        repo_rev_file_lines.extend(f"{s[0].decode()} {s[1].decode()}" for s in status)
    return repo_rev_file_lines


def add_agrif_files(run_desc, desc_file, run_set_dir, run_dir, nocheck_init):
    """Add file copies and symlinks to temporary run directory for
    AGRIF runs.

    :param dict run_desc: Run description dictionary.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param run_set_dir: Directory containing the run description file,
                        from which relative paths for the namelist section
                        files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress restart file existence check;
                                 the default is to check

    :raises: :py:exc:`SystemExit` with exit code 2 if mismatching number of
             sub-grids is detected
    """
    try:
        get_run_desc_value(run_desc, ("AGRIF",), fatal=False)
    except KeyError:
        # Not an AGRIF run
        return
    fixed_grids = get_run_desc_value(
        run_desc, ("AGRIF", "fixed grids"), run_dir, resolve_path=True
    )
    shutil.copy2(fspath(fixed_grids), fspath(run_dir / "AGRIF_FixedGrids.in"))
    # Get number of sub-grids
    n_sub_grids = 0
    with (run_dir / "AGRIF_FixedGrids.in").open("rt") as f:
        n_sub_grids = len(
            [line for line in f if not line.startswith("#") and len(line.split()) == 8]
        )
    run_desc_sections = {
        # sub-grid coordinates and bathymetry files
        "grid": functools.partial(make_grid_links, run_desc, run_dir),
        # sub-grid namelist files
        "namelists": functools.partial(make_namelists, run_set_dir, run_desc, run_dir),
        # sub-grid output files
        "output": functools.partial(
            copy_run_set_files, run_desc, desc_file, run_set_dir, run_dir
        ),
    }
    try:
        get_run_desc_value(run_desc, ("restart",), run_dir=run_dir, fatal=False)
        run_desc_sections["restart"] = functools.partial(
            make_restart_links, run_desc, run_dir, nocheck_init
        )
    except KeyError:
        # The parent grid is not being initialized from a restart file,
        # so the sub-grids can't be either
        pass
    for run_desc_section, func in run_desc_sections.items():
        sub_grids_count = 0
        section = get_run_desc_value(run_desc, (run_desc_section,))
        for key in section:
            if key.startswith("AGRIF"):
                sub_grids_count += 1
                agrif_n = int(key.split("_")[1])
                func(agrif_n=agrif_n)
        if sub_grids_count != n_sub_grids:
            logger.error(
                f"Expected {n_sub_grids} AGRIF sub-grids in {run_desc_section} section, "
                f"but found {sub_grids_count} - please check your run description file"
            )
            remove_run_dir(run_dir)
            raise SystemExit(2)
