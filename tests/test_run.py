# Copyright 2013-2021 The Salish Sea MEOPAR Contributors
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
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import cliff.app
import pytest
import yaml

import nemo_cmd.run


@pytest.fixture
def run_cmd():
    import nemo_cmd.run

    return nemo_cmd.run.Run(Mock(spec=cliff.app.App), [])


class TestParser:
    """Unit tests for `nemo run` sub-command command-line parser."""

    def test_get_parser(self, run_cmd):
        parser = run_cmd.get_parser("nemo run")
        assert parser.prog == "nemo run"

    def test_parsed_args_defaults(self, run_cmd):
        parser = run_cmd.get_parser("nemo run")
        parsed_args = parser.parse_args(["foo", "baz"])
        assert parsed_args.desc_file == Path("foo")
        assert parsed_args.results_dir == "baz"
        assert parsed_args.max_deflate_jobs == 4
        assert not parsed_args.nocheck_init
        assert not parsed_args.no_submit
        assert parsed_args.waitjob == 0
        assert parsed_args.queue_job_cmd == "qsub"
        assert not parsed_args.quiet

    @pytest.mark.parametrize(
        "flag, attr",
        [
            ("--nocheck-initial-conditions", "nocheck_init"),
            ("--no-submit", "no_submit"),
            ("-q", "quiet"),
            ("--quiet", "quiet"),
        ],
    )
    def test_parsed_args_boolean_flags(self, flag, attr, run_cmd):
        parser = run_cmd.get_parser("nemo run")
        parsed_args = parser.parse_args(["foo", "baz", flag])
        assert getattr(parsed_args, attr)

    @pytest.mark.parametrize("cmd", ["qsub", "sbatch"])
    def test_parsed_args_queue_job_cmd(self, cmd, run_cmd):
        parser = run_cmd.get_parser("nemo run")
        parsed_args = parser.parse_args(["foo", "baz", "--queue-job-cmd", cmd])
        assert parsed_args.queue_job_cmd == cmd

    def test_bad_queue_job_cmd(self, run_cmd):
        parser = run_cmd.get_parser("nemo run")
        with pytest.raises(SystemExit):
            parsed_args = parser.parse_args(["foo", "baz", "--queue-job-cmd", "fling"])


@patch("nemo_cmd.run.logger", autospec=True)
class TestTakeAction:
    """Unit tests for `salishsea run` sub-command take_action() method."""

    @patch("nemo_cmd.run.run", return_value="qsub message", autospec=True)
    def test_take_action(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file="desc file",
            results_dir="results dir",
            max_deflate_jobs=4,
            nocheck_init=False,
            no_deflate=False,
            no_submit=False,
            waitjob=0,
            queue_job_cmd="qsub",
            quiet=False,
        )
        run_cmd.run(parsed_args)
        m_run.assert_called_once_with(
            "desc file", "results dir", 4, False, False, False, 0, "qsub", quiet=False
        )
        m_logger.info.assert_called_once_with("qsub message")

    @patch("nemo_cmd.run.run", return_value="qsub message", autospec=True)
    def test_take_action_quiet(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file="desc file",
            results_dir="results dir",
            max_deflate_jobs=4,
            nocheck_init=False,
            no_deflate=False,
            no_submit=False,
            waitjob=0,
            queue_job_cmd="qsub",
            quiet=True,
        )
        run_cmd.run(parsed_args)
        assert not m_logger.info.called

    @patch("nemo_cmd.run.run", return_value=None, autospec=True)
    def test_take_action_no_submit(self, m_run, m_logger, run_cmd):
        parsed_args = SimpleNamespace(
            desc_file="desc file",
            results_dir="results dir",
            max_deflate_jobs=4,
            nocheck_init=False,
            no_deflate=False,
            no_submit=True,
            waitjob=0,
            queue_job_cmd="qsub",
            quiet=True,
        )
        run_cmd.run(parsed_args)
        assert not m_logger.info.called


@patch("nemo_cmd.run.subprocess.check_output", return_value="msg", autospec=True)
@patch("nemo_cmd.run._build_batch_script", return_value=u"script", autospec=True)
@patch("nemo_cmd.run.get_n_processors", return_value=144, autospec=True)
@patch("nemo_cmd.run.load_run_desc", spec=True)
@patch("nemo_cmd.run.api.prepare", spec=True)
class TestRun:
    """Unit tests for `salishsea run` run() function."""

    @pytest.mark.parametrize(
        "sep_xios_server, xios_servers, queue_job_cmd",
        [(None, 0, "qsub"), (False, 0, "qsub"), (True, 4, "sbatch")],
    )
    def test_run_submit(
        self,
        m_prepare,
        m_lrd,
        m_gnp,
        m_bbs,
        m_sco,
        sep_xios_server,
        xios_servers,
        queue_job_cmd,
        tmpdir,
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {
                "separate XIOS server": sep_xios_server,
                "XIOS servers": xios_servers,
            }
        }
        submit_job_msg = nemo_cmd.run.run(
            Path("nemo.yaml"), str(p_results_dir), queue_job_cmd=queue_job_cmd
        )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(str(p_run_dir)))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            [queue_job_cmd, "NEMO.sh"], universal_newlines=True
        )
        assert submit_job_msg == "msg"

    @pytest.mark.parametrize(
        "sep_xios_server, xios_servers, queue_job_cmd",
        [(None, 0, "qsub"), (False, 0, "qsub"), (True, 4, "sbatch")],
    )
    def test_run_no_submit(
        self,
        m_prepare,
        m_lrd,
        m_gnp,
        m_bbs,
        m_sco,
        sep_xios_server,
        xios_servers,
        queue_job_cmd,
        tmpdir,
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {
                "separate XIOS server": sep_xios_server,
                "XIOS servers": xios_servers,
            }
        }
        submit_job_msg = nemo_cmd.run.run(
            Path("nemo.yaml"),
            str(p_results_dir),
            no_submit=True,
            queue_job_cmd=queue_job_cmd,
        )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(str(p_run_dir)))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        assert not m_sco.called
        assert submit_job_msg is None

    @pytest.mark.parametrize(
        "xios_servers, queue_job_cmd", [(0, "qsub"), (4, "qsub"), (1, "sbatch")]
    )
    def test_run_no_deflate(
        self, m_prepare, m_lrd, m_gnp, m_bbs, m_sco, xios_servers, queue_job_cmd, tmpdir
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {"separate XIOS server": True, "XIOS servers": xios_servers}
        }
        submit_job_msg = nemo_cmd.run.run(
            Path("nemo.yaml"),
            str(p_results_dir),
            no_deflate=True,
            no_submit=False,
            queue_job_cmd=queue_job_cmd,
        )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(str(p_run_dir)))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            True,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            [queue_job_cmd, "NEMO.sh"], universal_newlines=True
        )
        assert submit_job_msg == "msg"

    @pytest.mark.parametrize(
        "sep_xios_server, xios_servers, queue_job_cmd",
        [(None, 0, "qsub"), (False, 0, "qsub"), (True, 4, "sbatch")],
    )
    def test_queue_job_cmd(
        self,
        m_prepare,
        m_lrd,
        m_gnp,
        m_bbs,
        m_sco,
        sep_xios_server,
        xios_servers,
        queue_job_cmd,
        tmpdir,
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {
                "separate XIOS server": sep_xios_server,
                "XIOS servers": xios_servers,
            }
        }
        submit_job_msg = nemo_cmd.run.run(
            Path("nemo.yaml"), str(p_results_dir), queue_job_cmd=queue_job_cmd
        )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(str(p_run_dir)))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            [queue_job_cmd, "NEMO.sh"], universal_newlines=True
        )
        assert submit_job_msg == "msg"

    @patch("nemo_cmd.run.logger", autospec=True)
    def test_unknown_queue_job_cmd(
        self, m_logger, m_prepare, m_lrd, m_gnp, m_bbs, m_sco, tmpdir
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {"separate XIOS server": True, "XIOS servers": 1}
        }
        queue_job_cmd = "fling"
        m_sco.side_effect = OSError
        submit_job_msg = nemo_cmd.run.run(
            Path("nemo.yaml"), str(p_results_dir), queue_job_cmd=queue_job_cmd
        )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(str(p_run_dir)))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            1,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            [queue_job_cmd, "NEMO.sh"], universal_newlines=True
        )
        assert m_logger.error.called
        assert submit_job_msg is None

    @pytest.mark.parametrize("sep_xios_server, xios_servers", [(False, 0), (True, 4)])
    def test_run_qsub_waitjob(
        self,
        m_prepare,
        m_lrd,
        m_gnp,
        m_bbs,
        m_sco,
        sep_xios_server,
        xios_servers,
        tmpdir,
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {
                "separate XIOS server": sep_xios_server,
                "XIOS servers": xios_servers,
            }
        }
        queue_job_cmd = "qsub"
        with patch("nemo_cmd.run.os.getenv", return_value="orcinus"):
            qsb_msg = nemo_cmd.run.run(
                Path("nemo.yaml"),
                str(p_results_dir),
                waitjob=42,
                queue_job_cmd=queue_job_cmd,
            )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(m_prepare()))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            ["qsub", "-W", "depend=afterok:42", "NEMO.sh"], universal_newlines=True
        )
        assert p_run_dir.join("NEMO.sh").check(file=True)
        assert qsb_msg == "msg"

    @pytest.mark.parametrize("sep_xios_server, xios_servers", [(False, 0), (True, 4)])
    def test_run_sbatch_waitjob(
        self,
        m_prepare,
        m_lrd,
        m_gnp,
        m_bbs,
        m_sco,
        sep_xios_server,
        xios_servers,
        tmpdir,
    ):
        p_run_dir = tmpdir.ensure_dir("run_dir")
        m_prepare.return_value = Path(str(p_run_dir))
        p_results_dir = tmpdir.ensure_dir("results_dir")
        m_lrd.return_value = {
            "output": {
                "separate XIOS server": sep_xios_server,
                "XIOS servers": xios_servers,
            }
        }
        queue_job_cmd = "sbatch"
        with patch("nemo_cmd.run.os.getenv", return_value="cedar"):
            qsb_msg = nemo_cmd.run.run(
                Path("nemo.yaml"),
                str(p_results_dir),
                waitjob=42,
                queue_job_cmd=queue_job_cmd,
            )
        m_prepare.assert_called_once_with(Path("nemo.yaml"), False)
        m_lrd.assert_called_once_with(Path("nemo.yaml"))
        m_gnp.assert_called_once_with(m_lrd(), Path(m_prepare()))
        m_bbs.assert_called_once_with(
            m_lrd(),
            "nemo.yaml",
            144,
            xios_servers,
            False,
            4,
            Path(str(p_results_dir)),
            Path(str(p_run_dir)),
            queue_job_cmd,
        )
        m_sco.assert_called_once_with(
            ["sbatch", "-d", "afterok:42", "NEMO.sh"], universal_newlines=True
        )
        assert p_run_dir.join("NEMO.sh").check(file=True)
        assert qsb_msg == "msg"


class TestBuiltBatchScript:
    """Unit tests for _build_batch_script() function."""

    @patch("nemo_cmd.run._cleanup", autospec=True)
    @patch("nemo_cmd.run._fix_permissions", autospec=True)
    @patch("nemo_cmd.run._execute", autospec=True)
    @patch("nemo_cmd.run._modules", autospec=True)
    @patch("nemo_cmd.run._definitions", autospec=True)
    @pytest.mark.parametrize(
        "queue_job_cmd, directives_func, no_deflate",
        [
            ("qsub", "nemo_cmd.run._pbs_directives", False),
            ("sbatch", "nemo_cmd.run._sbatch_directives", True),
        ],
    )
    def test_queue_job_cmd_directives(
        self,
        m_defns,
        m_mods,
        m_exec,
        m_fixperms,
        m_cleanup,
        queue_job_cmd,
        directives_func,
        no_deflate,
    ):
        p_dirs_func = patch(
            directives_func,
            autospec=True,
            return_value=directives_func.rsplit(".", 1)[1][1:],
        )
        run_desc = {"modules to load": []}
        desc_file = "NEMO.yaml"
        nemo_processors = 42
        xios_processors = 1
        max_deflate_jobs = 4
        results_dir = Path()
        run_dir = Path()
        with p_dirs_func as m_dirs_func:
            nemo_cmd.run._build_batch_script(
                run_desc,
                desc_file,
                nemo_processors,
                xios_processors,
                no_deflate,
                max_deflate_jobs,
                results_dir,
                run_dir,
                queue_job_cmd,
            )
            m_dirs_func.assert_called_once_with(
                run_desc, nemo_processors + xios_processors, results_dir
            )
        m_defns.assert_called_once_with(
            run_desc, desc_file, run_dir, results_dir, queue_job_cmd, no_deflate
        )
        m_mods.assert_called_once_with(run_desc["modules to load"])
        m_exec.assert_called_once_with(
            nemo_processors, xios_processors, no_deflate, max_deflate_jobs
        )
        m_fixperms.assert_called_once_with()
        m_cleanup.assert_called_once_with()

    @pytest.mark.parametrize("no_deflate", [True, False])
    def test_qsub(self, no_deflate):
        desc_file = StringIO(
            u"run_id: foo\n"
            u"walltime: 01:02:03\n"
            u"email: me@example.com\n"
            u"modules to load:\n"
            u"  - intel\n"
            u"  - intel/14.0/netcdf-4.3.3.1_mpi\n"
            u"  - intel/14.0/netcdf-fortran-4.4.0_mpi\n"
            u"  - intel/14.0/hdf5-1.8.15p1_mpi\n"
            u"  - intel/14.0/nco-4.5.2\n"
            u"  - python\n"
        )
        run_desc = yaml.safe_load(desc_file)
        script = nemo_cmd.run._build_batch_script(
            run_desc,
            "NEMO.yaml",
            nemo_processors=42,
            xios_processors=1,
            no_deflate=no_deflate,
            max_deflate_jobs=4,
            results_dir=Path("results_dir"),
            run_dir=Path(),
            queue_job_cmd="qsub",
        )
        expected = (
            u"#!/bin/bash\n"
            u"\n"
            u"#PBS -N foo\n"
            u"#PBS -S /bin/bash\n"
            u"#PBS -l procs=43\n"
            u"# memory per processor\n"
            u"#PBS -l pmem=2000mb\n"
            u"#PBS -l walltime=1:02:03\n"
            u"# email when the job [b]egins and [e]nds, or is [a]borted\n"
            u"#PBS -m bea\n"
            u"#PBS -M me@example.com\n"
            u"# stdout and stderr file paths/names\n"
            u"#PBS -o results_dir/stdout\n"
            u"#PBS -e results_dir/stderr\n"
            u"\n"
            u"\n"
            u'RUN_ID="foo"\n'
            u'RUN_DESC="NEMO.yaml"\n'
            u'WORK_DIR="."\n'
            u'RESULTS_DIR="results_dir"\n'
            u'COMBINE="${PBS_O_HOME}/.local/bin/nemo combine"\n'
        )
        if not no_deflate:
            expected += u'DEFLATE="${PBS_O_HOME}/.local/bin/nemo deflate"\n'
        expected += (
            u'GATHER="${PBS_O_HOME}/.local/bin/nemo gather"\n'
            u"\n"
            u"\n"
            u"module load intel\n"
            u"module load intel/14.0/netcdf-4.3.3.1_mpi\n"
            u"module load intel/14.0/netcdf-fortran-4.4.0_mpi\n"
            u"module load intel/14.0/hdf5-1.8.15p1_mpi\n"
            u"module load intel/14.0/nco-4.5.2\n"
            u"module load python\n"
            u"\n"
            u"\n"
            u"mkdir -p ${RESULTS_DIR}\n"
            u"\n"
            u"cd ${WORK_DIR}\n"
            u'echo "working dir: $(pwd)"\n'
            u"\n"
            u'echo "Starting run at $(date)"\n'
            u"mpirun -np 42 ./nemo.exe : -np 1 ./xios_server.exe\n"
            u"MPIRUN_EXIT_CODE=$?\n"
            u'echo "Ended run at $(date)"\n'
            u"\n"
            u'echo "Results combining started at $(date)"\n'
            u"${COMBINE} ${RUN_DESC} --debug\n"
            u'echo "Results combining ended at $(date)"\n'
        )
        if not no_deflate:
            expected += (
                u"\n"
                u'echo "Results deflation started at $(date)"\n'
                u"module load nco/4.6.6\n"
                u"${DEFLATE} *_grid_[TUVW]*.nc *_ptrc_T*.nc "
                u"--jobs 4 --debug\n"
                u'echo "Results deflation ended at $(date)"\n'
            )
        expected += (
            u"\n"
            u'echo "Results gathering started at $(date)"\n'
            u"${GATHER} ${RESULTS_DIR} --debug\n"
            u'echo "Results gathering ended at $(date)"\n'
            u"\n"
            u"chmod go+rx ${RESULTS_DIR}\n"
            u"chmod g+rw ${RESULTS_DIR}/*\n"
            u"chmod o+r ${RESULTS_DIR}/*\n"
            u"\n"
            u'echo "Deleting run directory" >>${RESULTS_DIR}/stdout\n'
            u"rmdir $(pwd)\n"
            u'echo "Finished at $(date)" >>${RESULTS_DIR}/stdout\n'
            u"exit ${MPIRUN_EXIT_CODE}\n"
        )
        assert script == expected

    @pytest.mark.parametrize("no_deflate", [True, False])
    def test_sbatch(self, no_deflate):
        desc_file = StringIO(
            u"run_id: foo\n"
            u"walltime: 01:02:03\n"
            u"email: me@example.com\n"
            u"account: rrg-allen\n"
            u"modules to load:\n"
            u"  - StdEnv/2020\n"
            u"  - netcdf-fortran-mpi/4.5.2\n"
            u"  - python/3.9.6\n"
        )
        run_desc = yaml.safe_load(desc_file)
        script = nemo_cmd.run._build_batch_script(
            run_desc,
            "NEMO.yaml",
            nemo_processors=42,
            xios_processors=1,
            no_deflate=no_deflate,
            max_deflate_jobs=4,
            results_dir=Path("results_dir"),
            run_dir=Path(),
            queue_job_cmd="sbatch",
        )
        expected = (
            u"#!/bin/bash\n"
            u"\n"
            u"#SBATCH --job-name=foo\n"
            u"#SBATCH --nodes=2\n"
            u"#SBATCH --ntasks-per-node=32\n"
            u"#SBATCH --mem=125G\n"
            u"#SBATCH --time=1:02:03\n"
            u"#SBATCH --mail-user=me@example.com\n"
            u"#SBATCH --mail-type=ALL\n"
            u"#SBATCH --account=rrg-allen\n"
            u"# stdout and stderr file paths/names\n"
            u"#SBATCH --output=results_dir/stdout\n"
            u"#SBATCH --error=results_dir/stderr\n"
            u"\n"
            u'RUN_ID="foo"\n'
            u'RUN_DESC="NEMO.yaml"\n'
            u'WORK_DIR="."\n'
            u'RESULTS_DIR="results_dir"\n'
            u'COMBINE="${HOME}/.local/bin/nemo combine"\n'
        )
        if not no_deflate:
            expected += u'DEFLATE="${HOME}/.local/bin/nemo deflate"\n'
        expected += (
            u'GATHER="${HOME}/.local/bin/nemo gather"\n'
            u"\n"
            u"\n"
            u"module load StdEnv/2020\n"
            u"module load netcdf-fortran-mpi/4.5.2\n"
            u"module load python/3.9.6\n"
            u"\n"
            u"\n"
            u"mkdir -p ${RESULTS_DIR}\n"
            u"\n"
            u"cd ${WORK_DIR}\n"
            u'echo "working dir: $(pwd)"\n'
            u"\n"
            u'echo "Starting run at $(date)"\n'
            u"mpirun -np 42 ./nemo.exe : -np 1 ./xios_server.exe\n"
            u"MPIRUN_EXIT_CODE=$?\n"
            u'echo "Ended run at $(date)"\n'
            u"\n"
            u'echo "Results combining started at $(date)"\n'
            u"${COMBINE} ${RUN_DESC} --debug\n"
            u'echo "Results combining ended at $(date)"\n'
        )
        if not no_deflate:
            expected += (
                u"\n"
                u'echo "Results deflation started at $(date)"\n'
                u"module load nco/4.6.6\n"
                u"${DEFLATE} *_grid_[TUVW]*.nc *_ptrc_T*.nc "
                u"--jobs 4 --debug\n"
                u'echo "Results deflation ended at $(date)"\n'
            )
        expected += (
            u"\n"
            u'echo "Results gathering started at $(date)"\n'
            u"${GATHER} ${RESULTS_DIR} --debug\n"
            u'echo "Results gathering ended at $(date)"\n'
            u"\n"
            u"chmod go+rx ${RESULTS_DIR}\n"
            u"chmod g+rw ${RESULTS_DIR}/*\n"
            u"chmod o+r ${RESULTS_DIR}/*\n"
            u"\n"
            u'echo "Deleting run directory" >>${RESULTS_DIR}/stdout\n'
            u"rmdir $(pwd)\n"
            u'echo "Finished at $(date)" >>${RESULTS_DIR}/stdout\n'
            u"exit ${MPIRUN_EXIT_CODE}\n"
        )
        assert script == expected


class TestPbsDirectives:
    """Unit tests for _pbs_directives() function."""

    run_desc = {
        "run_id": "test",
        "walltime": "1:24:42",
        "email": "somebody@example.com",
    }

    @patch("nemo_cmd.run.logger", autospec=True)
    @pytest.mark.parametrize("n_processors", [1, 32, 43])
    def test_pbs_directives(self, m_logger, n_processors):
        results_dir = Path()
        directives = nemo_cmd.run._pbs_directives(
            self.run_desc, n_processors, results_dir
        )
        expected = (
            u"#PBS -N test\n"
            u"#PBS -S /bin/bash\n"
            u"#PBS -l procs={n_processors}\n"
            u"# memory per processor\n"
            u"#PBS -l pmem=2000mb\n"
            u"#PBS -l walltime=1:24:42\n"
            u"# email when the job [b]egins and [e]nds, or is [a]borted\n"
            u"#PBS -m bea\n"
            u"#PBS -M {email}\n"
            u"# stdout and stderr file paths/names\n"
            u"#PBS -o ./stdout\n"
            u"#PBS -e ./stderr\n"
            u"\n"
        ).format(n_processors=n_processors, email=self.run_desc["email"])
        assert directives == expected


class TestPBS_Resources:
    """Unit tests for _pbs_resources() function."""

    @pytest.mark.parametrize(
        "resources, expected",
        [
            ([], u""),
            (["partition=QDR"], u"#PBS -l partition=QDR\n"),
            (
                ["partition=QDR", "feature=X5675"],
                u"#PBS -l partition=QDR\n#PBS -l feature=X5675\n",
            ),
        ],
    )
    def test_pbs_resources(self, resources, expected):
        pbs_resources = nemo_cmd.run._pbs_resources(resources, 11)
        assert pbs_resources == expected

    @pytest.mark.parametrize(
        "resources, n_procs, expected",
        [
            (["nodes=4:ppn=12"], 13, "#PBS -l nodes=2:ppn=12\n"),
            (["nodes=n:ppn=12"], 13, "#PBS -l nodes=2:ppn=12\n"),
        ],
    )
    def test_node_ppn_resource(self, resources, n_procs, expected):
        pbs_resources = nemo_cmd.run._pbs_resources(resources, n_procs)
        assert pbs_resources == expected


class TestSbatchDirectives:
    """Unit tests for _sbatch_directives() function."""

    run_desc = {
        "run_id": "test",
        "walltime": "1:24:42",
        "email": "somebody@example.com",
    }

    @patch("nemo_cmd.run.logger", autospec=True)
    @pytest.mark.parametrize("n_processors, n_nodes", [(1, 1), (32, 1), (43, 2)])
    def test_sbatch_directives(self, m_logger, n_processors, n_nodes):
        results_dir = Path()
        directives = nemo_cmd.run._sbatch_directives(
            self.run_desc, n_processors, results_dir
        )
        expected = (
            u"#SBATCH --job-name=test\n"
            u"#SBATCH --nodes={n_nodes}\n"
            u"#SBATCH --ntasks-per-node=32\n"
            u"#SBATCH --mem=125G\n"
            u"#SBATCH --time=1:24:42\n"
            u"#SBATCH --mail-user={email}\n"
            u"#SBATCH --mail-type=ALL\n"
            u"# stdout and stderr file paths/names\n"
            u"#SBATCH --output=stdout\n"
            u"#SBATCH --error=stderr\n"
        ).format(n_nodes=n_nodes, email=self.run_desc["email"])
        assert directives == expected
        assert m_logger.warning.called

    @patch("nemo_cmd.run.logger", autospec=True)
    def test_account_directive(self, m_logger):
        results_dir = Path()
        with patch.dict(self.run_desc, account="def-allen"):
            directives = nemo_cmd.run._sbatch_directives(self.run_desc, 43, results_dir)
        assert u"#SBATCH --account=def-allen\n" in directives
        assert not m_logger.warning.called


class TestDefinitions:
    """Unit tests for _definitions() function."""

    @pytest.mark.parametrize(
        "queue_job_cmd, nemo_bin, no_deflate",
        [
            ("qsub", "${PBS_O_HOME}/.local/bin/nemo", False),
            ("sbatch", "${HOME}/.local/bin/nemo", True),
        ],
    )
    def test_nemo_cmd(self, queue_job_cmd, nemo_bin, no_deflate):
        run_desc = {"run_id": "test"}
        defns = nemo_cmd.run._definitions(
            run_desc,
            "NEMO.yaml",
            Path("run_dir"),
            Path("results_dir"),
            queue_job_cmd,
            no_deflate,
        )
        expected = (
            u'RUN_ID="test"\n'
            u'RUN_DESC="NEMO.yaml"\n'
            u'WORK_DIR="run_dir"\n'
            u'RESULTS_DIR="results_dir"\n'
            u'COMBINE="{nemo_bin} combine"\n'
        ).format(nemo_bin=nemo_bin)
        if not no_deflate:
            expected += u'DEFLATE="{nemo_bin} deflate"\n'.format(nemo_bin=nemo_bin)
        expected += u'GATHER="{nemo_bin} gather"\n'.format(nemo_bin=nemo_bin)
        assert defns == expected


class TestModules:
    """Unit tests for _module() function."""

    @pytest.mark.parametrize(
        "modules, expected",
        [
            ([], u""),
            (["intel"], u"module load intel\n"),
            (["intel", "python"], u"module load intel\nmodule load python\n"),
        ],
    )
    def test_module(self, modules, expected):
        module_loads = nemo_cmd.run._modules(modules)
        assert module_loads == expected


class TestCleanup:
    """Unit test for _cleanup() function."""

    def test_cleanup(self):
        script = nemo_cmd.run._cleanup()
        expected = """echo "Deleting run directory" >>${RESULTS_DIR}/stdout
        rmdir $(pwd)
        echo "Finished at $(date)" >>${RESULTS_DIR}/stdout
        exit ${MPIRUN_EXIT_CODE}
        """
        expected = expected.splitlines()
        for i, line in enumerate(script.splitlines()):
            assert line.strip() == expected[i].strip()
