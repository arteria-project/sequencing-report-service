
import pytest

import mock

import time

from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.models.db_models import Job, Status

from tests.test_utils import mock_job_repo as mock_job_repo_cm
from tests.test_utils import create_mock_nextflow_job_factory


class TestLocalRunnerService(object):

    @pytest.fixture
    def nextflow_cmd_generator(self):
        return create_mock_nextflow_job_factory()

    def test_schedule(self, nextflow_cmd_generator):
        with mock_job_repo_cm() as (mock_job_repo, mock_job_repo_factory):
            job = Job(runfolder='foo_folder', job_id=1)
            local_runner_service = LocalRunnerService(mock_job_repo_factory, nextflow_cmd_generator)
            local_runner_service.schedule(job)
            mock_job_repo.add_job.assert_called_once()

    def test_process_job_queue(self, nextflow_cmd_generator):
        with mock_job_repo_cm() as (mock_job_repo, mock_job_repo_factory):
            job = Job(runfolder='foo_folder')
            local_runner_service = LocalRunnerService(mock_job_repo_factory, nextflow_cmd_generator)
            local_runner_service.schedule(job)
            local_runner_service.process_job_queue()
            assert local_runner_service._currently_running_job is not None

            local_runner_service.process_job_queue()
            assert local_runner_service._currently_running_job is None
            _, call_keywords = mock_job_repo.set_state_of_job.call_args
            assert 'cmd_log' in call_keywords

    def test_stop(self, nextflow_cmd_generator):
        with mock_job_repo_cm() as (mock_job_repo, mock_job_repo_factory):
            job = Job(runfolder='foo_folder', status=Status.PENDING)
            mock_job_repo.get_job = mock.MagicMock(return_value=job)

            def mock_job_status_set(job_id, status):
                job.status = status
                return job

            mock_job_repo.set_state_of_job = mock.MagicMock(side_effect=mock_job_status_set)
            local_runner_service = LocalRunnerService(mock_job_repo_factory, nextflow_cmd_generator)
            job_id = local_runner_service.stop(job.job_id)

            assert job.status == Status.CANCELLED
