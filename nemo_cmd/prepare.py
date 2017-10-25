# Copyright 2013-2017 The Salish Sea MEOPAR Contributors
# and The University of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""NEMO-Cmd command plug-in for prepare sub-command.

Sets up the necessary symbolic links for a NEMO run
in a specified directory and changes the pwd to that directory.
"""
from copy import copy
import functools
import logging
import os
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
import shutil
import time
import xml.etree.ElementTree

import arrow
import cliff.command
from dateutil import tz
import hglib

from nemo_cmd import lib, fspath, resolved_path, expanded_path
from nemo_cmd.combine import find_rebuild_nemo_script
from nemo_cmd.namelist import namelist2dict, get_namelist_value

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Prepare(cliff.command.Command):
    """Prepare a NEMO run
    """

    def get_parser(self, prog_name):
        parser = super(Prepare, self).get_parser(prog_name)
        parser.description = '''
            Set up the NEMO run described in DESC_FILE
            and print the path to the run directory.
        '''
        parser.add_argument(
            'desc_file',
            metavar='DESC_FILE',
            type=Path,
            help='run description YAML file'
        )
        parser.add_argument(
            '--nocheck-initial-conditions',
            dest='nocheck_init',
            action='store_true',
            help='''
            Suppress checking of the initial conditions link.
            Useful if you are submitting a job to an HPC qsub queue and want
            the submitted job to wait for completion of a previous job.
            '''
        )
        parser.add_argument(
            '--nemo3.4',
            dest='nemo34',
            action='store_true',
            help='''
            Prepare a NEMO-3.4 run;
            the default is to prepare a NEMO-3.6 run.
            '''
        )
        parser.add_argument(
            '-q',
            '--quiet',
            action='store_true',
            help="don't show the run directory path on completion"
        )
        return parser

    def take_action(self, parsed_args):
        """Execute the `nemo prepare` sub-command.

        A UUID named directory is created and symbolic links are created
        in the directory to the files and directories specified to run NEMO.
        The path to the run directory is logged to the console on completion
        of the set-up.
        """
        run_dir = prepare(
            parsed_args.desc_file, parsed_args.nemo34, parsed_args.nocheck_init
        )
        if not parsed_args.quiet:
            logger.info('Created run directory {}'.format(run_dir))
        return run_dir


def prepare(desc_file, nemo34, nocheck_init):
    """Create and prepare the temporary run directory.

    The temporary run directory is created with a UUID as its name.
    Symbolic links are created in the directory to the files and
    directories specified to run NEMO.
    The path to the run directory is returned.

    :param desc_file: File path/name of the YAML run description file.
    :type desc_file: :py:class:`pathlib.Path`

    :param boolean nemo34: Prepare a NEMO-3.4 run;
                           the default is to prepare a NEMO-3.6 run

    :param boolean nocheck_init: Suppress initial condition link check;
                                 the default is to check

    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_desc = lib.load_run_desc(desc_file)
    nemo_bin_dir = _check_nemo_exec(run_desc, nemo34)
    xios_bin_dir = _check_xios_exec(run_desc) if not nemo34 else ''
    find_rebuild_nemo_script(run_desc)
    run_set_dir = resolved_path(desc_file).parent
    run_dir = _make_run_dir(run_desc)
    _make_namelists(run_set_dir, run_desc, run_dir, nemo34)
    _copy_run_set_files(run_desc, desc_file, run_set_dir, run_dir, nemo34)
    _make_executable_links(nemo_bin_dir, run_dir, nemo34, xios_bin_dir)
    _make_grid_links(run_desc, run_dir)
    _make_forcing_links(run_desc, run_dir, nemo34, nocheck_init)
    if not nemo34:
        _make_restart_links(run_desc, run_dir, nocheck_init)
    _record_vcs_revisions(run_desc, run_dir)
    if not nemo34:
        _add_agrif_files(
            run_desc, desc_file, run_set_dir, run_dir, nocheck_init
        )
    return run_dir


def get_run_desc_value(
    run_desc,
    keys,
    expand_path=False,
    resolve_path=False,
    run_dir=None,
    fatal=True
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
            '"{}" key not found - please check your run description YAML file'
            .format(': '.join(keys))
        )
        if run_dir:
            _remove_run_dir(run_dir)
        raise SystemExit(2)
    if expand_path:
        value = expanded_path(value)
    if resolve_path:
        value = resolved_path(value)
        if not value.exists():
            logger.error(
                '{path} path from "{keys}" key not found - please check your '
                'run description YAML file'.format(
                    path=value, keys=': '.join(keys)
                )
            )
            if run_dir:
                _remove_run_dir(run_dir)
            raise SystemExit(2)
    return value


def _check_nemo_exec(run_desc, nemo34):
    """Calculate absolute path of the NEMO executable's directory.

    Confirm that the NEMO executable exists, raising a SystemExit
    exception if it does not.

    For NEMO-3.4 runs, confirm check that the IOM server executable
    exists, issuing a warning if it does not.

    :param dict run_desc: Run description dictionary.

    :param boolean nemo34: Prepare a NEMO-3.4 run;
                           the default is to prepare a NEMO-3.6 run

    :returns: Absolute path of NEMO executable's directory.
    :rtype: :py:class:`pathlib.Path`

    :raises: SystemExit
    """
    try:
        nemo_config_dir = get_run_desc_value(
            run_desc, ('paths', 'NEMO code config'),
            resolve_path=True,
            fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        nemo_config_dir = get_run_desc_value(
            run_desc, ('paths', 'NEMO-code-config'), resolve_path=True
        )
    try:
        config_name = get_run_desc_value(
            run_desc, ('config name',), fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        config_name = get_run_desc_value(run_desc, ('config_name',))
    nemo_bin_dir = nemo_config_dir / config_name / 'BLD' / 'bin'
    nemo_exec = nemo_bin_dir / 'nemo.exe'
    if not nemo_exec.exists():
        logger.error(
            '{} not found - did you forget to build it?'.format(nemo_exec)
        )
        raise SystemExit(2)
    if nemo34:
        iom_server_exec = nemo_bin_dir / 'server.exe'
        if not iom_server_exec.exists():
            logger.warning(
                '{} not found - are you running without key_iomput?'
                .format(iom_server_exec)
            )
    return nemo_bin_dir


def _check_xios_exec(run_desc):
    """Calculate absolute path of the XIOS executable's directory.

    Confirm that the XIOS executable exists, raising a SystemExit
    exception if it does not.

    :param dict run_desc: Run description dictionary.

    :returns: Absolute path of XIOS executable's directory.
    :rtype: :py:class:`pathlib.Path`

    :raises: SystemExit
    """
    xios_code_path = get_run_desc_value(
        run_desc, ('paths', 'XIOS'), resolve_path=True
    )
    xios_bin_dir = xios_code_path / 'bin'
    xios_exec = xios_bin_dir / 'xios_server.exe'
    if not xios_exec.exists():
        logger.error(
            '{} not found - did you forget to build it?'.format(xios_exec)
        )
        raise SystemExit(2)
    return xios_bin_dir


def _make_run_dir(run_desc):
    """Create the temporary directory from which NEMO will be run.

    The location is in the runs directory from the run description,
    and its name is the run id combined with an ISO-format date/time stamp.

    :param dict run_desc: Run description dictionary.
    
    :returns: Path of the temporary run directory
    :rtype: :py:class:`pathlib.Path`
    """
    run_id = get_run_desc_value(run_desc, ('run_id',))
    runs_dir = get_run_desc_value(
        run_desc, ('paths', 'runs directory'), resolve_path=True
    )
    run_dir = runs_dir / '{run_id}_{timestamp}'.format(
        run_id=run_id,
        timestamp=arrow.now().format('YYYY-MM-DDTHHmmss.SSSSSSZ')
    )
    run_dir.mkdir()
    return run_dir


def _remove_run_dir(run_dir):
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


def _make_namelists(run_set_dir, run_desc, run_dir, nemo34):
    """Build the namelist file(s) for the run in run_dir by concatenating
    the list(s) of namelist section files provided in run_desc.

    If any of the required namelist section files are missing,
    delete the run directory and raise a SystemExit exception.

    :param run_set_dir: Directory containing the run description file,
                        from which relative paths for the namelist section
                        files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nemo34: Prepare a NEMO-3.4 run;
                           the default is to prepare a NEMO-3.6 run

    :raises: SystemExit
    """
    if nemo34:
        _make_namelist_nemo34(run_set_dir, run_desc, run_dir)
    else:
        _make_namelists_nemo36(run_set_dir, run_desc, run_dir)


def _make_namelist_nemo34(run_set_dir, run_desc, run_dir):
    """Build the namelist file for the NEMO-3.4 run in run_dir by
    concatenating the list of namelist section files provided in run_desc.

    If any of the required namelist section files are missing,
    delete the run directory and raise a SystemExit exception.

    :param run_set_dir: Directory containing the run description file,
                        from which relative paths for the namelist section
                        files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: SystemExit
    """
    namelists = get_run_desc_value(run_desc, ('namelists',), run_dir=run_dir)
    namelist_filename = 'namelist'
    with (run_dir / namelist_filename).open('wt') as namelist:
        for nl in namelists:
            try:
                with (run_set_dir / nl).open('rt') as f:
                    namelist.writelines(f.readlines())
                    namelist.write(u'\n\n')
            except IOError as e:
                logger.error(e)
                _remove_run_dir(run_dir)
                raise SystemExit(2)
        namelist.writelines(EMPTY_NAMELISTS)
    _set_mpi_decomposition(namelist_filename, run_desc, run_dir)


def _make_namelists_nemo36(run_set_dir, run_desc, run_dir, agrif_n=None):
    """Build the namelist files for the NEMO-3.6 run in run_dir by
    concatenating the lists of namelist section files provided in run_desc.

    If any of the required namelist section files are missing,
    delete the run directory and raise a SystemExit exception.

    :param run_set_dir: Directory containing the run description file,
                      from which relative paths for the namelist section
                      files start.
    :type run_set_dir: :py:class:`pathlib.Path`

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.

    :raises: SystemExit
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend NEMO-Cmd

    try:
        nemo_code_config = run_desc['paths']['NEMO code config']
    except KeyError:
        # Alternate key spelling for backward compatibility
        nemo_code_config = run_desc['paths']['NEMO-code-config']
    nemo_config_dir = resolved_path(nemo_code_config)
    try:
        config_name = run_desc['config name']
    except KeyError:
        # Alternate key spelling for backward compatibility
        config_name = run_desc['config_name']
    keys = ('namelists',)
    if agrif_n is not None:
        keys = ('namelists', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n))
    namelists = get_run_desc_value(run_desc, keys, run_dir=run_dir)
    for namelist_filename in namelists:
        if namelist_filename.startswith('AGRIF'):
            continue
        namelist_dest = namelist_filename
        keys = ('namelists', namelist_filename)
        if agrif_n is not None:
            namelist_dest = '{agrif_n}_{namelist_filename}'.format(
                agrif_n=agrif_n, namelist_filename=namelist_filename
            )
            keys = (
                'namelists', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n),
                namelist_filename
            )
        with (run_dir / namelist_dest).open('wt') as namelist:
            namelist_files = get_run_desc_value(
                run_desc, keys, run_dir=run_dir
            )
            for nl in namelist_files:
                nl_path = expanded_path(nl)
                if not nl_path.is_absolute():
                    nl_path = run_set_dir / nl_path
                try:
                    with nl_path.open('rt') as f:
                        namelist.writelines(f.readlines())
                        namelist.write(u'\n\n')
                except IOError as e:
                    logger.error(e)
                    _remove_run_dir(run_dir)
                    raise SystemExit(2)
        ref_namelist = namelist_filename.replace('_cfg', '_ref')
        if ref_namelist not in namelists:
            ref_namelist_source = (
                nemo_config_dir / config_name / 'EXP00' / ref_namelist
            )
            shutil.copy2(
                fspath(ref_namelist_source),
                fspath(run_dir / namelist_dest.replace('_cfg', '_ref'))
            )
    if 'namelist_cfg' in namelists:
        _set_mpi_decomposition('namelist_cfg', run_desc, run_dir)
    else:
        logger.error(
            'No namelist_cfg key found in namelists section of run '
            'description'
        )
        raise SystemExit(2)


def _set_mpi_decomposition(namelist_filename, run_desc, run_dir):
    """Update the &nammpp namelist jpni & jpnj values with the MPI
    decomposition values from the run description.

    A SystemExit exception is raise if there is no MPI decomposition
    specified in the run description.

    :param str namelist_filename: The name of the namelist file.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: SystemExit
    """
    try:
        jpni, jpnj = get_run_desc_value(
            run_desc, ('MPI decomposition',), fatal=False
        ).split('x')
    except KeyError:
        logger.error(
            'MPI decomposition value not found in YAML run description file. '
            'Please add a line like:\n'
            '  MPI decomposition: 8x18\n'
            'that says how you want the domain distributed over the '
            'processors in the i (longitude) and j (latitude) dimensions.'
        )
        _remove_run_dir(run_dir)
        raise SystemExit(2)
    with (run_dir / namelist_filename).open('rt') as f:
        lines = f.readlines()
    for key, new_value in {'jpni': jpni, 'jpnj': jpnj}.items():
        value, i = get_namelist_value(key, lines)
        lines[i] = lines[i].replace(value, new_value)
    with (run_dir / namelist_filename).open('wt') as f:
        f.writelines(lines)


def _copy_run_set_files(
    run_desc, desc_file, run_set_dir, run_dir, nemo34, agrif_n=None
):
    """Copy the run-set files given into run_dir.

    For all versions of NEMO the YAML run description file 
    (from the command-line) is copied.
    The IO defs file is also copied.
    The file path/name of the IO defs file is taken from the :kbd:`output`
    stanza of the YAML run description file.
    The IO defs file is copied as :file:`iodef.xml` because that is the
    name that NEMO-3.4 or XIOS expects.

    For NEMO-3.4, the :file:`xmlio_server.def` file is also copied.

    For NEMO-3.6, the domain defs and field defs files used by XIOS
    are also copied.
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

    :param boolean nemo34: Prepare a NEMO-3.4 run;
                           the default is to prepare a NEMO-3.6 run

    :param int agrif_n: AGRIF sub-grid number.
    """
    try:
        iodefs = get_run_desc_value(
            run_desc, ('output', 'iodefs'),
            resolve_path=True,
            run_dir=run_dir,
            fatal=False
        )
    except KeyError:
        # Alternate key spelling for backward compatibility
        iodefs = get_run_desc_value(
            run_desc, ('output', 'files'), resolve_path=True, run_dir=run_dir
        )
    run_set_files = [
        (iodefs, 'iodef.xml'),
        (run_set_dir / desc_file.name, desc_file.name),
    ]
    if nemo34:
        run_set_files.append(
            (run_set_dir / 'xmlio_server.def', 'xmlio_server.def')
        )
    else:
        try:
            keys = ('output', 'domaindefs')
            domain_def_filename = 'domain_def.xml'
            if agrif_n is not None:
                keys = (
                    'output', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n),
                    'domaindefs'
                )
                domain_def_filename = '{agrif_n}_domain_def.xml'.format(
                    agrif_n=agrif_n
                )
            domains_def = get_run_desc_value(
                run_desc,
                keys,
                resolve_path=True,
                run_dir=run_dir,
                fatal=False,
            )
        except KeyError:
            # Alternate key spelling for backward compatibility
            keys = ('output', 'domain')
            if agrif_n is not None:
                keys = (
                    'output', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n),
                    'domain'
                )
            domains_def = get_run_desc_value(
                run_desc, keys, resolve_path=True, run_dir=run_dir
            )
        try:
            fields_def = get_run_desc_value(
                run_desc, ('output', 'fielddefs'),
                resolve_path=True,
                run_dir=run_dir,
                fatal=False
            )
        except KeyError:
            # Alternate key spelling for backward compatibility
            fields_def = get_run_desc_value(
                run_desc, ('output', 'fields'),
                resolve_path=True,
                run_dir=run_dir
            )
        run_set_files.extend([
            (domains_def, domain_def_filename),
            (fields_def, 'field_def.xml'),
        ])
        try:
            keys = ('output', 'filedefs')
            file_def_filename = 'file_def.xml'
            if agrif_n is not None:
                keys = (
                    'output', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n),
                    'filedefs'
                )
                file_def_filename = '{agrif_n}_file_def.xml'.format(
                    agrif_n=agrif_n
                )
            files_def = get_run_desc_value(
                run_desc,
                keys,
                resolve_path=True,
                run_dir=run_dir,
                fatal=False
            )
            run_set_files.append((files_def, file_def_filename))
        except KeyError:
            # `files` key is optional and only used with XIOS-2
            pass
    for source, dest_name in run_set_files:
        shutil.copy2(fspath(source), fspath(run_dir / dest_name))
    if not nemo34:
        _set_xios_server_mode(run_desc, run_dir)


def _set_xios_server_mode(run_desc, run_dir):
    """Update the :file:`iodef.xml` :kbd:`xios` context :kbd:`using_server`
    variable text with the :kbd:`separate XIOS server` value from the
    run description.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: SystemExit
    """
    try:
        sep_xios_server = get_run_desc_value(
            run_desc, ('output', 'separate XIOS server'), fatal=False
        )
    except KeyError:
        logger.error(
            'separate XIOS server key/value not found in output section '
            'of YAML run description file. '
            'Please add lines like:\n'
            '  separate XIOS server: True\n'
            '  XIOS servers: 1\n'
            'that say whether to run the XIOS server(s) attached or detached, '
            'and how many of them to use.'
        )
        _remove_run_dir(run_dir)
        raise SystemExit(2)
    tree = xml.etree.ElementTree.parse(fspath(run_dir / 'iodef.xml'))
    root = tree.getroot()
    using_server = root.find(
        'context[@id="xios"]//variable[@id="using_server"]'
    )
    using_server.text = 'true' if sep_xios_server else 'false'
    using_server_line = xml.etree.ElementTree.tostring(using_server).decode()
    with (run_dir / 'iodef.xml').open('rt') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'using_server' in line:
            lines[i] = using_server_line
            break
    with (run_dir / 'iodef.xml').open('wt') as f:
        f.writelines(lines)


def _make_executable_links(nemo_bin_dir, run_dir, nemo34, xios_bin_dir):
    """Create symlinks in run_dir to the NEMO and I/O server executables
    and record the code repository revision(s) used for the run.

    :param nemo_bin_dir: Absolute path of directory containing NEMO executable.
    :type nemo_bin_dir: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nemo34: Make executable links for a NEMO-3.4 run
                           if :py:obj:`True`,
                           otherwise make links for a NEMO-3.6 run.

    :param xios_bin_dir: Absolute path of directory containing XIOS executable.
    :type xios_bin_dir: :py:class:`pathlib.Path`
    """
    nemo_exec = nemo_bin_dir / 'nemo.exe'
    (run_dir / 'nemo.exe').symlink_to(nemo_exec)
    iom_server_exec = nemo_bin_dir / 'server.exe'
    if nemo34 and iom_server_exec.exists():
        (run_dir / 'server.exe').symlink_to(iom_server_exec)
    if not nemo34:
        xios_server_exec = xios_bin_dir / 'xios_server.exe'
        (run_dir / 'xios_server.exe').symlink_to(xios_server_exec)


def _make_grid_links(run_desc, run_dir, agrif_n=None):
    """Create symlinks in run_dir to the file names that NEMO expects
    to the bathymetry and coordinates files given in the run_desc dict.

    For AGRIF sub-grids, the symlink names are prefixed with the agrif_n;
    e.g. 1_coordinates.nc.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param int agrif_n: AGRIF sub-grid number.

    :raises: SystemExit
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend NEMO-Cmd

    coords_keys = ('grid', 'coordinates')
    coords_filename = 'coordinates.nc'
    bathy_keys = ('grid', 'bathymetry')
    bathy_filename = 'bathy_meter.nc'
    if agrif_n is not None:
        coords_keys = (
            'grid', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n), 'coordinates'
        )
        coords_filename = '{agrif_n}_coordinates.nc'.format(agrif_n=agrif_n)
        bathy_keys = (
            'grid', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n), 'bathymetry'
        )
        bathy_filename = '{agrif_n}_bathy_meter.nc'.format(agrif_n=agrif_n)
    coords_path = get_run_desc_value(
        run_desc, coords_keys, expand_path=True, run_dir=run_dir
    )
    bathy_path = get_run_desc_value(
        run_desc, bathy_keys, expand_path=True, run_dir=run_dir
    )
    if coords_path.is_absolute() and bathy_path.is_absolute():
        grid_paths = ((coords_path, coords_filename),
                      (bathy_path, bathy_filename))
    else:
        nemo_forcing_dir = get_run_desc_value(
            run_desc, ('paths', 'forcing'), resolve_path=True, run_dir=run_dir
        )
        grid_dir = nemo_forcing_dir / 'grid'
        grid_paths = ((grid_dir / coords_path, coords_filename),
                      (grid_dir / bathy_path, bathy_filename))
    for source, link_name in grid_paths:
        if not source.exists():
            logger.error(
                '{} not found; cannot create symlink - '
                'please check the forcing path and grid file names '
                'in your run description file'.format(source)
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)
        (run_dir / link_name).symlink_to(source)


def _make_forcing_links(run_desc, run_dir, nemo34, nocheck_init):
    """Create symlinks in run_dir to the forcing directory/file names,
    and record the NEMO-forcing repo revision used for the run.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nemo34: Make forcing links for a NEMO-3.4 run
                           if :py:obj:`True`,
                           otherwise make links for a NEMO-3.6 run.

    :param boolean nocheck_init: Suppress initial condition link check
                                 the default is to check

    :raises: :py:exc:`SystemExit` if the NEMO-forcing repo path does not
             exist
    """
    if nemo34:
        _make_forcing_links_nemo34(run_desc, run_dir, nocheck_init)
    else:
        _make_forcing_links_nemo36(run_desc, run_dir)


def _make_forcing_links_nemo34(run_desc, run_dir, nocheck_init):
    """For a NEMO-3.4 run, create symlinks in run_dir to the forcing
    directory/file names that the Salish Sea model uses by convention.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress initial condition link check;
                                 the default is to check

    :raises: :py:exc:`SystemExit` if a symlink target does not exist
    """
    symlinks = []
    init_conditions = _resolve_forcing_path(
        run_desc, ('initial conditions',), run_dir
    )
    link_name = (
        'restart.nc'
        if 'restart' in fspath(init_conditions) else 'initial_strat'
    )
    if not init_conditions.exists() and not nocheck_init:
        logger.error(
            '{} not found; cannot create symlink - '
            'please check the forcing path and initial conditions file names '
            'in your run description file'.format(init_conditions)
        )
        _remove_run_dir(run_dir)
        raise SystemExit(2)
    symlinks.append((init_conditions, link_name))
    atmospheric = _resolve_forcing_path(run_desc, ('atmospheric',), run_dir)
    open_boundaries = _resolve_forcing_path(
        run_desc, ('open boundaries',), run_dir
    )
    rivers = _resolve_forcing_path(run_desc, ('rivers',), run_dir)
    forcing_dirs = ((atmospheric, 'NEMO-atmos'),
                    (open_boundaries, 'open_boundaries'), (rivers, 'rivers'))
    for source, link_name in forcing_dirs:
        if not source.exists():
            logger.error(
                '{} not found; cannot create symlink - '
                'please check the forcing paths and file names '
                'in your run description file'.format(source)
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)
        (run_dir / link_name).symlink_to(source)
    _check_atmos_files(run_desc, run_dir)


def _resolve_forcing_path(run_desc, keys, run_dir):
    """Calculate a resolved path for a forcing path.

    If the path in the run description is absolute, resolve any symbolic links,
    etc. in it.

    If the path is relative, append it to the NEMO-forcing repo path from the
    run description.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param tuple keys: Key sequence in the :kbd:`forcing` section of the 
                       run description for which the resolved path calculated.

    :param str run_dir: Path of the temporary run directory.

    :return: Resolved path
    :rtype: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` if the NEMO-forcing repo path does not exist
    """
    path = get_run_desc_value(
        run_desc, (('forcing',) + keys), expand_path=True, fatal=False
    )
    if path.is_absolute():
        return path.resolve()
    nemo_forcing_dir = get_run_desc_value(
        run_desc, ('paths', 'forcing'), resolve_path=True, run_dir=run_dir
    )
    return nemo_forcing_dir / path


def _make_forcing_links_nemo36(run_desc, run_dir):
    """For a NEMO-3.6 run, create symlinks in run_dir to the forcing
    directory/file names given in the run description forcing section.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` if a symlink target does not exist
    """
    link_checkers = {'atmospheric': _check_atmospheric_forcing_link}
    link_names = get_run_desc_value(run_desc, ('forcing',), run_dir=run_dir)
    for link_name in link_names:
        source = _resolve_forcing_path(
            run_desc, (link_name, 'link to'), run_dir
        )
        if not source.exists():
            logger.error(
                '{} not found; cannot create symlink - '
                'please check the forcing paths and file names '
                'in your run description file'.format(source)
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)
        (run_dir / link_name).symlink_to(source)
        try:
            link_checker = get_run_desc_value(
                run_desc, ('forcing', link_name, 'check link'),
                run_dir=run_dir,
                fatal=False
            )
            link_checkers[link_checker['type']](
                run_dir, source, link_checker['namelist filename']
            )
        except KeyError:
            if 'check link' not in link_names[link_name]:
                # No forcing link checker specified
                pass
            else:
                if link_checker is not None:
                    logger.error(
                        'unknown forcing link checker: {}'
                        .format(link_checker)
                    )
                    _remove_run_dir(run_dir)
                    raise SystemExit(2)


def _check_atmospheric_forcing_link(run_dir, link_path, namelist_filename):
    """Confirm that the atmospheric forcing files necessary for the NEO-3.6 run
    are present.

    Sections of the namelist file are parsed to determine
    the necessary files, and the date ranges required for the run.
    
    This is the atmospheric forcing link check function used for NEMO-3.6 runs.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    
    :param :py:class:`pathlib.Path` link_path: Path of the atmospheric forcing
                                               files collection.
    
    :param str namelist_filename: File name of the namelist to parse for
                                  atmospheric file names and date ranges.

    :raises: :py:exc:`SystemExit` if an atmospheric forcing file does not exist
    """
    namelist = namelist2dict(fspath(run_dir / namelist_filename))
    if not namelist['namsbc'][0]['ln_blk_core']:
        return
    start_date = arrow.get(str(namelist['namrun'][0]['nn_date0']), 'YYYYMMDD')
    it000 = namelist['namrun'][0]['nn_it000']
    itend = namelist['namrun'][0]['nn_itend']
    dt = namelist['namdom'][0]['rn_rdt']
    end_date = start_date.replace(seconds=(itend - it000) * dt - 1)
    qtys = (
        'sn_wndi sn_wndj sn_qsr sn_qlw sn_tair sn_humi sn_prec sn_snow'.split()
    )
    core_dir = namelist['namsbc_core'][0]['cn_dir']
    file_info = {
        'core': {
            'dir': core_dir,
            'params': [],
        },
    }
    for qty in qtys:
        flread_params = namelist['namsbc_core'][0][qty]
        file_info['core']['params'].append(
            (flread_params[0], flread_params[5])
        )
    if namelist['namsbc'][0]['ln_apr_dyn']:
        apr_dir = namelist['namsbc_apr'][0]['cn_dir']
        file_info['apr'] = {
            'dir': apr_dir,
            'params': [],
        }
        flread_params = namelist['namsbc_apr'][0]['sn_apr']
        file_info['apr']['params'].append((flread_params[0], flread_params[5]))
    startm1 = start_date.replace(days=-1)
    for r in arrow.Arrow.range('day', startm1, end_date):
        for v in file_info.values():
            for basename, period in v['params']:
                if period == 'daily':
                    file_path = os.path.join(
                        v['dir'], '{basename}_'
                        'y{date.year}m{date.month:02d}d{date.day:02d}.nc'
                        .format(basename=basename, date=r)
                    )
                elif period == 'yearly':
                    file_path = os.path.join(
                        v['dir'], '{basename}.nc'.format(basename=basename)
                    )
                if not (run_dir / file_path).exists():
                    logger.error(
                        '{file_path} not found; '
                        'please confirm that atmospheric forcing files '
                        'for {startm1} through '
                        '{end} are in the {dir} collection, '
                        'and that atmospheric forcing paths in your '
                        'run description and surface boundary conditions '
                        'namelist are in agreement.'.format(
                            file_path=file_path,
                            startm1=startm1.format('YYYY-MM-DD'),
                            end=end_date.format('YYYY-MM-DD'),
                            dir=link_path
                        )
                    )
                    _remove_run_dir(run_dir)
                    raise SystemExit(2)


def _check_atmos_files(run_desc, run_dir):
    """Confirm that the atmospheric forcing files necessary for the NEO-3.4 run
    are present. Sections of the namelist file are parsed to determine
    the necessary files, and the date ranges required for the run.

    This is the atmospheric forcing link check function used for NEMO-3.4 runs.
    
    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :raises: :py:exc:`SystemExit` if an atmospheric forcing file does not exist
    """
    namelist = namelist2dict(fspath(run_dir / 'namelist'))
    if not namelist['namsbc'][0]['ln_blk_core']:
        return
    date0 = arrow.get(str(namelist['namrun'][0]['nn_date0']), 'YYYYMMDD')
    it000 = namelist['namrun'][0]['nn_it000']
    itend = namelist['namrun'][0]['nn_itend']
    dt = namelist['namdom'][0]['rn_rdt']
    start_date = date0.replace(seconds=it000 * dt - 1)
    end_date = date0.replace(seconds=itend * dt - 1)
    qtys = (
        'sn_wndi sn_wndj sn_qsr sn_qlw sn_tair sn_humi sn_prec sn_snow'.split()
    )
    core_dir = namelist['namsbc_core'][0]['cn_dir']
    file_info = {
        'core': {
            'dir': core_dir,
            'params': [],
        },
    }
    for qty in qtys:
        flread_params = namelist['namsbc_core'][0][qty]
        file_info['core']['params'].append(
            (flread_params[0], flread_params[5])
        )
    if namelist['namsbc'][0]['ln_apr_dyn']:
        apr_dir = namelist['namsbc_apr'][0]['cn_dir']
        file_info['apr'] = {
            'dir': apr_dir,
            'params': [],
        }
        flread_params = namelist['namsbc_apr'][0]['sn_apr']
        file_info['apr']['params'].append((flread_params[0], flread_params[5]))
    startm1 = start_date.replace(days=-1)
    for r in arrow.Arrow.range('day', startm1, end_date):
        for v in file_info.values():
            for basename, period in v['params']:
                if period == 'daily':
                    file_path = os.path.join(
                        v['dir'], '{basename}_'
                        'y{date.year}m{date.month:02d}d{date.day:02d}.nc'
                        .format(basename=basename, date=r)
                    )
                elif period == 'yearly':
                    file_path = os.path.join(
                        v['dir'], '{basename}.nc'.format(basename=basename)
                    )
                if not (run_dir / file_path).exists():
                    nemo_forcing_dir = get_run_desc_value(
                        run_desc, ('paths', 'forcing'),
                        resolve_path=True,
                        run_dir=run_dir
                    )
                    atmos_dir = _resolve_forcing_path(
                        run_desc, ('atmospheric',), run_dir
                    )
                    logger.error(
                        '{file_path} not found; '
                        'please confirm that atmospheric forcing files '
                        'for {startm1} through '
                        '{end} are in the {dir} collection, '
                        'and that atmospheric forcing paths in your '
                        'run description and surface boundary conditions '
                        'namelist are in agreement.'.format(
                            file_path=file_path,
                            startm1=startm1.format('YYYY-MM-DD'),
                            end=end_date.format('YYYY-MM-DD'),
                            dir=nemo_forcing_dir / atmos_dir,
                        )
                    )
                    _remove_run_dir(run_dir)
                    raise SystemExit(2)


def _make_restart_links(run_desc, run_dir, nocheck_init, agrif_n=None):
    """For a NEMO-3.6 run, create symlinks in run_dir to the restart
    files given in the run description restart section.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :param boolean nocheck_init: Suppress restart file existence check;
                                 the default is to check

    :param int agrif_n: AGRIF sub-grid number.

    :raises: :py:exc:`SystemExit` if a symlink target does not exist
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend NEMO-Cmd

    keys = ('restart',)
    if agrif_n is not None:
        keys = ('restart', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n))
    try:
        link_names = get_run_desc_value(
            run_desc, keys, run_dir=run_dir, fatal=False
        )
    except KeyError:
        logger.warning(
            'No restart section found in run description YAML file, '
            'so proceeding on the assumption that initial conditions '
            'have been provided'
        )
        return
    for link_name in link_names:
        if link_name.startswith('AGRIF'):
            continue
        keys = ('restart', link_name)
        if agrif_n is not None:
            keys = (
                'restart', 'AGRIF_{agrif_n}'.format(agrif_n=agrif_n), link_name
            )
            link_name = '{agrif_n}_{link_name}'.format(
                agrif_n=agrif_n, link_name=link_name
            )
        source = get_run_desc_value(run_desc, keys, expand_path=True)
        if not source.exists() and not nocheck_init:
            logger.error(
                '{} not found; cannot create symlink - '
                'please check the restart file paths and file names '
                'in your run description file'.format(source)
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)
        if nocheck_init:
            (run_dir / link_name).symlink_to(source)
        else:
            (run_dir / link_name).symlink_to(source.resolve())


def _record_vcs_revisions(run_desc, run_dir):
    """Record revision and status information from version control system
    repositories in files in the temporary run directory.

    :param dict run_desc: Run description dictionary.

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`
    """
    if 'vcs revisions' not in run_desc:
        return
    vcs_funcs = {'hg': get_hg_revision}
    vcs_tools = get_run_desc_value(
        run_desc, ('vcs revisions',), run_dir=run_dir
    )
    for vcs_tool in vcs_tools:
        repos = get_run_desc_value(
            run_desc, ('vcs revisions', vcs_tool), run_dir=run_dir
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
        rev_file = run_dir / '{repo.name}_rev.txt'.format(repo=repo_path)
        with rev_file.open('wt') as f:
            f.writelines(u'{}\n'.format(line) for line in repo_rev_file_lines)


def get_hg_revision(repo, run_dir):
    """Gather revision and status information from Mercurial repo.

    Effectively record the output of :command:`hg parents -v` and
    :param run_dir:
    :command:`hg status -mardC`.
    
    Files named :file:`CONFIG/cfg.txt` and 
    :file:`TOOLS/COMPILE/full_key_list.txt` are ignored because they change
    frequently but the changes generally of no consequence;
    see https://bitbucket.org/salishsea/nemo-cmd/issues/18.

    :param repo: Path of Mercurial repository to get revision and status
                 information from.
    :type repo: :py:class:`pathlib.Path`

    :param run_dir: Path of the temporary run directory.
    :type run_dir: :py:class:`pathlib.Path`

    :returns: Mercurial repository revision and status information strings.
    :rtype: list
    """
    if not repo.exists():
        logger.warning(
            'revision and status requested for non-existent repo: {repo}'
            .format(repo=repo)
        )
        return []
    repo_path = copy(repo)
    while str(repo) != repo_path.root:
        try:
            with hglib.open(fspath(repo)) as hg:
                parents = hg.parents()
                files = [f[1] for f in hg.status(change=[parents[0].rev])]
                status = hg.status(
                    modified=True,
                    added=True,
                    removed=True,
                    deleted=True,
                    copies=True
                )
            break
        except hglib.error.ServerError:
            repo = repo.parent
    else:
        logger.error(
            'unable to find Mercurial repo root in or above '
            '{repo_path}'.format(repo_path=repo_path)
        )
        _remove_run_dir(run_dir)
        raise SystemExit(2)
    revision = parents[0]
    repo_rev_file_lines = [
        'changset:   {rev}:{node}'.format(
            rev=revision.rev.decode(), node=revision.node.decode()
        )
    ]
    if revision.tags:
        repo_rev_file_lines.append(
            'tag:        {tags}'.format(tags=revision.tags.decode())
        )
    if len(parents) > 1:
        repo_rev_file_lines.extend(
            'parent:     {rev}:{node}'.format(
                rev=parent.rev.decode(), node=parent.node.decode()
            ) for parent in parents
        )
    date = arrow.get(revision.date).replace(tzinfo=tz.tzlocal())
    repo_rev_file_lines.extend([
        'user:       {}'.format(revision.author.decode()),
        'date:       {}'.format(date.format('ddd MMM DD HH:mm:ss YYYY ZZ')),
        'files:      {}'.format(' '.join(f.decode() for f in files)),
        'description:',
    ])
    repo_rev_file_lines.extend(
        line.decode() for line in revision.desc.splitlines()
    )
    ignore = (u'CONFIG/cfg.txt', u'TOOLS/COMPILE/full_key_list.txt')
    for s in copy(status):
        if s[1].decode().endswith(ignore):
            status.remove(s)
    if status:
        logger.warning(
            'There are uncommitted changes in {}'.format(resolved_path(repo))
        )
        repo_rev_file_lines.append('uncommitted changes:')
        repo_rev_file_lines.extend(
            '{code} {path}'.format(code=s[0].decode(), path=s[1].decode())
            for s in status
        )
    return repo_rev_file_lines


def _add_agrif_files(run_desc, desc_file, run_set_dir, run_dir, nocheck_init):
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

    :raises: SystemExit if mismatching number of sub-grids is detected
    """

    ##TODO: Refactor this into a public function that can be used by prepare
    ## plug-ins in packages like SalishSeaCmd that extend NEMO-Cmd

    try:
        get_run_desc_value(run_desc, ('AGRIF',), fatal=False)
    except KeyError:
        # Not an AGRIF run
        return
    fixed_grids = get_run_desc_value(
        run_desc, ('AGRIF', 'fixed grids'), run_dir, resolve_path=True
    )
    shutil.copy2(fspath(fixed_grids), fspath(run_dir / 'AGRIF_FixedGrids.in'))
    # Get number of sub-grids
    n_sub_grids = 0
    with (run_dir / 'AGRIF_FixedGrids.in').open('rt') as f:
        n_sub_grids = len([
            line for line in f
            if not line.startswith('#') and len(line.split()) == 8
        ])
    run_desc_sections = {
        # sub-grid coordinates and bathymetry files
        'grid':
        functools.partial(_make_grid_links, run_desc, run_dir),
        # sub-grid restart files
        'restart':
        functools.partial(
            _make_restart_links, run_desc, run_dir, nocheck_init
        ),
        # sub-grid namelist files
        'namelists':
        functools.partial(
            _make_namelists_nemo36, run_set_dir, run_desc, run_dir
        ),
        # sub-grid output files
        'output':
        functools.partial(
            _copy_run_set_files,
            run_desc,
            desc_file,
            run_set_dir,
            run_dir,
            nemo34=False
        ),
    }
    for run_desc_section, func in run_desc_sections.items():
        sub_grids_count = 0
        section = get_run_desc_value(run_desc, (run_desc_section,))
        for key in section:
            if key.startswith('AGRIF'):
                sub_grids_count += 1
                agrif_n = int(key.split('_')[1])
                func(agrif_n=agrif_n)
        if sub_grids_count != n_sub_grids:
            logger.error(
                'Expected {n_sub_grids} AGRIF sub-grids in {section} section, '
                'but found {sub_grids_count} - '
                'please check your run description file'.format(
                    n_sub_grids=n_sub_grids,
                    section=run_desc_section,
                    sub_grids_count=sub_grids_count
                )
            )
            _remove_run_dir(run_dir)
            raise SystemExit(2)


# All of the namelists that NEMO-3.4 requires, but empty so that they result
# in the defaults defined in the NEMO code being used.
EMPTY_NAMELISTS = u"""
&namrun        !  Parameters of the run
&end
&nam_diaharm   !  Harmonic analysis of tidal constituents ('key_diaharm')
&end
&namzgr        !  Vertical coordinate
&end
&namzgr_sco    !  s-Coordinate or hybrid z-s-coordinate
&end
&namdom        !  Space and time domain (bathymetry, mesh, timestep)
&end
&namtsd        !  Data : Temperature  & Salinity
&end
&namsbc        !  Surface Boundary Condition (surface module)
&end
&namsbc_ana    !  Analytical surface boundary condition
&end
&namsbc_flx    !  Surface boundary condition : flux formulation
&end
&namsbc_clio   !  CLIO bulk formulae
&end
&namsbc_core   !  CORE bulk formulae
&end
&namsbc_mfs    !  MFS bulk formulae
&end
&namtra_qsr    !  Penetrative solar radiation
&end
&namsbc_rnf    !  Runoffs namelist surface boundary condition
&end
&namsbc_apr    !  Atmospheric pressure used as ocean forcing or in bulk
&end
&namsbc_ssr    !  Surface boundary condition : sea surface restoring
&end
&namsbc_alb    !  Albedo parameters
&end
&namlbc        !  Lateral momentum boundary condition
&end
&namcla        !  Cross land advection
&end
&nam_tide      !  Tide parameters (#ifdef key_tide)
&end
&nambdy        !  Unstructured open boundaries ("key_bdy")
&end
&nambdy_index  !  Open boundaries - definition ("key_bdy")
&end
&nambdy_dta    !  Open boundaries - external data ("key_bdy")
&end
&nambdy_tide   !  Tidal forcing at open boundaries
&end
&nambfr        !  Bottom friction
&end
&nambbc        !  Bottom temperature boundary condition
&end
&nambbl        !  Bottom boundary layer scheme
&end
&nameos        !  Ocean physical parameters
&end
&namtra_adv    !  Advection scheme for tracer
&end
&namtra_ldf    !  Lateral diffusion scheme for tracers
&end
&namtra_dmp    !  Tracer: T & S newtonian damping
&end
&namdyn_adv    !  Formulation of the momentum advection
&end
&namdyn_vor    !  Option of physics/algorithm (not control by CPP keys)
&end
&namdyn_hpg    !  Hydrostatic pressure gradient option
&end
&namdyn_ldf    !  Lateral diffusion on momentum
&end
&namzdf        !  Vertical physics
&end
&namzdf_gls    !  GLS vertical diffusion ("key_zdfgls")
&end
&namsol        !  Elliptic solver / island / free surface
&end
&nammpp        !  Massively Parallel Processing ("key_mpp_mpi)
&end
&namctl        !  Control prints & Benchmark
&end
&namnc4        !  netCDF4 chunking and compression settings ("key_netcdf4")
&end
&namptr        !  Poleward Transport Diagnostic
&end
&namhsb        !  Heat and salt budgets
&end
&namdct        !  Transports through sections
&end
&namsbc_wave   !  External fields from wave model
&end
&namdyn_nept   !  Neptune effect
&end           !  (simplified: lateral & vertical diffusions removed)
&namtrj        !  Handling non-linear trajectory for TAM
&end           !  (output for direct model, input for TAM)
"""
