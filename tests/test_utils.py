import contextlib
import mock

from sequencing_report_service.repositiories.job_repo import JobRepository
from sequencing_report_service.nextflow import NextflowCommandGenerator

@contextlib.contextmanager
def mock_job_repo():
    _mock_job_repo = mock.create_autospec(JobRepository, session_factory=None)
    _mock_job_repo.__enter__.return_value = _mock_job_repo

    def return_job_repo_factory():
        return _mock_job_repo

    yield _mock_job_repo, return_job_repo_factory


def create_mock_nextflow_job_factory():
    m = mock.create_autospec(NextflowCommandGenerator)
    m.command.return_value = ['echo', 'hello']
    return m