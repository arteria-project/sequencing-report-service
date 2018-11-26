
import pytest


import mock

import time

from sequencing_report_service.repositiories.job_repo import JobRepository
from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.models.db_models import Job, Status


class TestLocalRunnerService(object):

    def test_schedule(self):
        mock_job_repo = mock.create_autospec(JobRepository)
        job = Job(runfolder='foo_folder')
        local_runner_service = LocalRunnerService(mock_job_repo)
        local_runner_service.schedule(job)
        mock_job_repo.add_job.assert_called_once()

    def test_process_job_queue(self):
        mock_job_repo = mock.create_autospec(JobRepository)
        job = Job(runfolder='foo_folder')
        local_runner_service = LocalRunnerService(mock_job_repo)
        local_runner_service.schedule(job)
        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is not None

        time.sleep(1.2)
        local_runner_service.process_job_queue()
        assert local_runner_service._currently_running_job is None

    def test_stop(self):
        mock_job_repo = mock.create_autospec(JobRepository)
        job = Job(runfolder='foo_folder', status=Status.PENDING)
        mock_job_repo.get_job = mock.MagicMock(return_value=job)

        def mock_job_status_set(job_id, status):
            job.status = status
            return job

        mock_job_repo.set_state_of_job = mock.MagicMock(side_effect=mock_job_status_set)
        local_runner_service = LocalRunnerService(mock_job_repo)
        job = local_runner_service.stop(job.job_id)

        assert job.status == Status.CANCELLED
