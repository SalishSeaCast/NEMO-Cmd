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
"""NEMO-Cmd run sub-command plug-in unit tests
"""
try:
    from pathlib import Path
except ImportError:
    # Python 2.7
    from pathlib2 import Path
try:
    from types import SimpleNamespace
except ImportError:
    # Python 2.7
    class SimpleNamespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)


try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import cliff.app
import pytest

import nemo_cmd.run


@pytest.fixture
def run_cmd():
    import nemo_cmd.run
    return nemo_cmd.run.Run(Mock(spec=cliff.app.App), [])


class TestParser:
    """Unit tests for `nemo run` sub-command command-line parser.
    """

    def test_get_parser(self, run_cmd):
        parser = run_cmd.get_parser('nemo run')
        assert parser.prog == 'nemo run'

    def test_parsed_args_defaults(self, run_cmd):
        parser = run_cmd.get_parser('nemo run')
        parsed_args = parser.parse_args(['foo', 'baz'])
        assert parsed_args.desc_file == Path('foo')
        assert parsed_args.results_dir == 'baz'
        assert parsed_args.max_deflate_jobs == 4
        assert not parsed_args.nemo34
        assert not parsed_args.nocheck_init
        assert not parsed_args.no_submit
        assert parsed_args.waitjob == 0
        assert parsed_args.queue_job_cmd == 'qsub'
        assert not parsed_args.quiet

    @pytest.mark.parametrize(
        'flag, attr', [
            ('--nemo3.4', 'nemo34'),
            ('--nocheck-initial-conditions', 'nocheck_init'),
            ('--no-submit', 'no_submit'),
            ('-q', 'quiet'),
            ('--quiet', 'quiet'),
        ]
    )
    def test_parsed_args_boolean_flags(self, flag, attr, run_cmd):
        parser = run_cmd.get_parser('nemo run')
        parsed_args = parser.parse_args(['foo', 'baz', flag])
        assert getattr(parsed_args, attr)

    @pytest.mark.parametrize('cmd', [
        'qsub',
        'sbatch',
    ])
    def test_parsed_args_queue_job_cmd(self, cmd, run_cmd):
        parser = run_cmd.get_parser('nemo run')
        parsed_args = parser.parse_args(['foo', 'baz', '--queue-job-cmd', cmd])
        assert parsed_args.queue_job_cmd == cmd

    def test_bad_queue_job_cmd(self, run_cmd):
        parser = run_cmd.get_parser('nemo run')
        with pytest.raises(SystemExit):
            parsed_args = parser.parse_args(
                ['foo', 'baz', '--queue-job-cmd', 'fling']
            )


@patch('nemo_cmd.run.logger')
class TestTakeAction:
    """Unit tests for `salishsea run` sub-command take_action() method.
    """

    @patch('nemo_cmd.run.run', return_value='qsub message')
    def test_take_action(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file='desc file',
            results_dir='results dir',
            max_deflate_jobs=4,
            nemo34=False,
            nocheck_init=False,
            no_submit=False,
            waitjob=0,
            queue_job_cmd='qsub',
            quiet=False
        )
        run_cmd.run(parsed_args)
        m_run.assert_called_once_with(
            'desc file',
            'results dir',
            4,
            False,
            False,
            False,
            0,
            'qsub',
            quiet=False
        )
        m_logger.info.assert_called_once_with('qsub message')

    @patch('nemo_cmd.run.run', return_value='qsub message')
    def test_take_action_quiet(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file='desc file',
            results_dir='results dir',
            max_deflate_jobs=4,
            nemo34=False,
            nocheck_init=False,
            no_submit=False,
            waitjob=0,
            queue_job_cmd='qsub',
            quiet=True
        )
        run_cmd.run(parsed_args)
        assert not m_logger.info.called

    @patch('nemo_cmd.run.run', return_value=None)
    def test_take_action_no_submit(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file='desc file',
            results_dir='results dir',
            max_deflate_jobs=4,
            nemo34=False,
            nocheck_init=False,
            no_submit=True,
            waitjob=0,
            queue_job_cmd='qsub',
            quiet=True
        )
        run_cmd.run(parsed_args)
        assert not m_logger.info.called


@patch('nemo_cmd.run.subprocess.check_output', return_value='msg')
@patch('nemo_cmd.run._build_batch_script', return_value=u'script')
@patch('nemo_cmd.run.lib.get_n_processors', return_value=144)
@patch('nemo_cmd.run.lib.load_run_desc')
@patch('nemo_cmd.run.api.prepare')
class TestRun:
    """Unit tests for `salishsea run` run() function.
    """

    @pytest.mark.parametrize(
        'nemo34, sep_xios_server, xios_servers', [
            (True, None, 0),
            (False, False, 0),
            (False, True, 4),
        ]
    )
    def test_run_submit(
        self, m_prepare, m_lrd, m_gnp, m_bbs, m_sco, nemo34, sep_xios_server,
        xios_servers, tmpdir
    ):
        p_run_dir = tmpdir.ensure_dir('run_dir')
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir('results_dir')
        if not nemo34:
            m_lrd.return_value = {
                'output': {
                    'separate XIOS server': sep_xios_server,
                    'XIOS servers': xios_servers,
                }
            }
        qsb_msg = nemo_cmd.run.run(
            Path('nemo.yaml'), str(p_results_dir), nemo34=nemo34
        )
        m_prepare.assert_called_once_with(Path('nemo.yaml'), nemo34, False)
        m_lrd.assert_called_once_with(Path('nemo.yaml'))
        m_gnp.assert_called_once_with(m_lrd())
        m_bbs.assert_called_once_with(
            m_lrd(), 'nemo.yaml', 144, xios_servers, 4,
            Path(str(p_results_dir)), Path(str(p_run_dir))
        )
        m_sco.assert_called_once_with(['qsub', 'NEMO.sh'],
                                      universal_newlines=True)
        assert qsb_msg == 'msg'

    @pytest.mark.parametrize(
        'nemo34, sep_xios_server, xios_servers', [
            (True, None, 0),
            (False, False, 0),
            (False, True, 4),
        ]
    )
    def test_run_no_submit(
        self, m_prepare, m_lrd, m_gnp, m_bbs, m_sco, nemo34, sep_xios_server,
        xios_servers, tmpdir
    ):
        p_run_dir = tmpdir.ensure_dir('run_dir')
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir('results_dir')
        if not nemo34:
            m_lrd.return_value = {
                'output': {
                    'separate XIOS server': sep_xios_server,
                    'XIOS servers': xios_servers,
                }
            }
        qsb_msg = nemo_cmd.run.run(
            Path('nemo.yaml'),
            str(p_results_dir),
            nemo34=nemo34,
            no_submit=True
        )
        m_prepare.assert_called_once_with(Path('nemo.yaml'), nemo34, False)
        m_lrd.assert_called_once_with(Path('nemo.yaml'))
        m_gnp.assert_called_once_with(m_lrd())
        m_bbs.assert_called_once_with(
            m_lrd(), 'nemo.yaml', 144, xios_servers, 4,
            Path(str(p_results_dir)), Path(str(p_run_dir))
        )
        assert not m_sco.called
        assert qsb_msg is None

        @pytest.mark.parametrize(
            'nemo34, sep_xios_server, xios_servers, queue_job_cmd', [
                (True, None, 0, 'qsub'),
                (False, False, 0, 'qsub'),
                (False, True, 4, 'sbatch'),
            ]
        )
        def test_queue_job_cmd(
            self, m_prepare, m_lrd, m_gnp, m_bbs, m_sco, nemo34,
            sep_xios_server, xios_servers, queue_job_cmd, tmpdir
        ):
            p_run_dir = tmpdir.ensure_dir('run_dir')
            m_prepare.return_value = Path(str(p_run_dir))
            p_results_dir = tmpdir.ensure_dir('results_dir')
            if not nemo34:
                m_lrd.return_value = {
                    'output': {
                        'separate XIOS server': sep_xios_server,
                        'XIOS servers': xios_servers,
                    }
                }
            qsb_msg = nemo_cmd.run.run(
                Path('nemo.yaml'), str(p_results_dir), nemo34=nemo34
            )
            m_prepare.assert_called_once_with(Path('nemo.yaml'), nemo34, False)
            m_lrd.assert_called_once_with(Path('nemo.yaml'))
            m_gnp.assert_called_once_with(m_lrd())
            m_bbs.assert_called_once_with(
                m_lrd(), 'nemo.yaml', 144, xios_servers, 4,
                Path(str(p_results_dir)), Path(str(p_run_dir))
            )
            m_sco.assert_called_once_with([queue_job_cmd, 'NEMO.sh'],
                                          universal_newlines=True)
            assert qsb_msg == 'msg'


class TestPBS_Resources:
    """Unit tests for _pbs_resources() function.
    """

    @pytest.mark.parametrize(
        'resources, expected', [
            ([], u''),
            (['partition=QDR'], u'#PBS -l partition=QDR\n'),
            (['partition=QDR', 'feature=X5675'],
             u'#PBS -l partition=QDR\n#PBS -l feature=X5675\n'),
        ]
    )
    def test_pbs_resources(self, resources, expected):
        pbs_resources = nemo_cmd.run._pbs_resources(resources, 11)
        assert pbs_resources == expected

    @pytest.mark.parametrize(
        'resources, n_procs, expected', [
            (['nodes=4:ppn=12'], 13, '#PBS -l nodes=2:ppn=12\n'),
            (['nodes=n:ppn=12'], 13, '#PBS -l nodes=2:ppn=12\n'),
        ]
    )
    def test_node_ppn_resource(self, resources, n_procs, expected):
        pbs_resources = nemo_cmd.run._pbs_resources(resources, n_procs)
        assert pbs_resources == expected


class TestModules:
    """Unit tests for _module() function.
    """

    @pytest.mark.parametrize(
        'modules, expected', [
            ([], u''),
            (['intel'], u'module load intel\n'),
            (['intel', 'python'], u'module load intel\nmodule load python\n'),
        ]
    )
    def test_module(self, modules, expected):
        module_loads = nemo_cmd.run._modules(modules)
        assert module_loads == expected


class TestCleanup:
    """Unit test for _cleanup() function.
    """

    def test_cleanup(self):
        script = nemo_cmd.run._cleanup()
        expected = '''echo "Deleting run directory" >>${RESULTS_DIR}/stdout
        rmdir $(pwd)
        echo "Finished at $(date)" >>${RESULTS_DIR}/stdout
        exit ${MPIRUN_EXIT_CODE}
        '''
        expected = expected.splitlines()
        for i, line in enumerate(script.splitlines()):
            assert line.strip() == expected[i].strip()
