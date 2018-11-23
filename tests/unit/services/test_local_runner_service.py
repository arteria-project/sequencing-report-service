
import pytest


import mock

import time

from sequencing_report_service.repositiories.job_repo import JobRepository
from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.models.db_models import Job


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
