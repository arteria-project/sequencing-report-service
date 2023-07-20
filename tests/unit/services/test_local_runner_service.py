
import pytest

import asyncio
import mock
import tempfile
import os
import time

from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.models.db_models import Job, State

from tests.test_utils import MockJobRepository
from tests.test_utils import create_mock_nextflow_job_factory


class TestLocalRunnerService(object):

    @pytest.fixture
    def nextflow_cmd_generator(self):
        return create_mock_nextflow_job_factory()

    @pytest.fixture
    def job_repo_factory(self):
        data = []

        def f():
            return MockJobRepository(data)
        return f

    @pytest.fixture
    def nextflow_log_dirs(self):
        return tempfile.mkdtemp()

    @pytest.mark.asyncio
    async def test_start(
            self,
            nextflow_cmd_generator,
            job_repo_factory,
            nextflow_log_dirs,
            ):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(
            job_repo_factory,
            nextflow_cmd_generator,
            nextflow_log_dirs,
        )
        command, environment = nextflow_cmd_generator.command(runfolder).values()

        with mock.patch("subprocess.Popen"):
            job_id = local_runner_service.start(runfolder)

        assert isinstance(local_runner_service.get_job(job_id), Job)

    def test_stop(
            self,
            nextflow_cmd_generator,
            job_repo_factory,
            nextflow_log_dirs
        ):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory,
                                                  nextflow_cmd_generator,
                                                  nextflow_log_dirs)
        job_id = local_runner_service.start(runfolder)
        time.sleep(1)
        stopped_id = local_runner_service.stop(job_id)

        assert local_runner_service.get_job(stopped_id).state == State.CANCELLED
        assert stopped_id == job_id
