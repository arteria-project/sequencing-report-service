
import pytest

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

    def test_schedule(self, nextflow_cmd_generator, job_repo_factory, nextflow_log_dirs):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory,
                                                  nextflow_cmd_generator,
                                                  nextflow_log_dirs)
        job_id = local_runner_service.schedule(runfolder)
        assert isinstance(local_runner_service.get_job(job_id), Job)

    def test_process_job_queue(self, nextflow_cmd_generator, job_repo_factory, nextflow_log_dirs):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory,
                                                  nextflow_cmd_generator,
                                                  nextflow_log_dirs)
        local_runner_service.schedule(runfolder)
        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is not None

        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is None

    def test_stop(self, nextflow_cmd_generator, job_repo_factory, nextflow_log_dirs):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory,
                                                  nextflow_cmd_generator,
                                                  nextflow_log_dirs)
        job_id = local_runner_service.schedule(runfolder)
        stopped_id = local_runner_service.stop(job_id)

        assert local_runner_service.get_job(stopped_id).state == State.CANCELLED
        assert stopped_id == job_id

    def test_error(self, job_repo_factory, nextflow_log_dirs):
        runfolder = 'foo_runfolder'
        local_runner_service = LocalRunnerService(job_repo_factory,
                                                  create_mock_nextflow_job_factory(error=True),
                                                  nextflow_log_dirs)
        job_id = local_runner_service.schedule(runfolder)
        local_runner_service.process_job_queue()
        time.sleep(1)
        local_runner_service.process_job_queue()
        assert local_runner_service.get_job(job_id).state == State.ERROR
