import contextlib
import mock

from sequencing_report_service.repositiories.job_repo import JobRepository
from sequencing_report_service.nextflow import NextflowCommandGenerator
from sequencing_report_service.models.db_models import Job, Status


def create_mock_nextflow_job_factory():
    m = mock.create_autospec(NextflowCommandGenerator)
    m.command.return_value = ['echo', 'hello']
    return m


class MockJobRepository():
    def __init__(self, data):
        self._jobs = data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def add_job(self, command):
        job = Job(command=command,
                  status=Status.PENDING,
                  job_id=len(self._jobs) + 1)
        self._jobs.append(job)
        return job

    def get_jobs(self):
        return self._jobs

    def get_jobs_with_status(self, status):
        return [i for i in self._jobs if i.status == status]

    def get_job(self, job_id):
        for job in self._jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_one_pending_job(self):
        potential_job = self.get_jobs_with_status(Status.PENDING)
        if potential_job[0]:
            return potential_job[0]

    def expunge_object(self, obj):
        return obj

    def set_state_of_job(self, job_id, state, cmd_log=None):
        job = self.get_job(job_id)
        job.status = state
        if cmd_log:
            job.log = cmd_log
        return job

    def set_pid_of_job(self, job_id, pid):
        job = self.get_job(job_id)
        job.pid = pid
        return Job

    def clear_out_stale_jobs_at_startup(self):
        stale_jobs = self.get_jobs_with_status(Status.STARTED)
        for job in stale_jobs:
            self.set_state_of_job(job_id=job.job_id, state=Status.CANCELLED)
