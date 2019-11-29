
import pytest

import mock

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

    def test_schedule(self, nextflow_cmd_generator, job_repo_factory):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory, nextflow_cmd_generator)
        job_id = local_runner_service.schedule(runfolder)
        assert isinstance(local_runner_service.get_job(job_id), Job)

    def test_process_job_queue(self, nextflow_cmd_generator, job_repo_factory):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory, nextflow_cmd_generator)
        local_runner_service.schedule(runfolder)
        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is not None

        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is None

    def test_stop(self, nextflow_cmd_generator, job_repo_factory):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory, nextflow_cmd_generator)
        job_id = local_runner_service.schedule(runfolder)
        stopped_id = local_runner_service.stop(job_id)

        assert local_runner_service.get_job(stopped_id).state == State.CANCELLED
        assert stopped_id == job_id
