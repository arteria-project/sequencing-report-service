import contextlib
import mock

from sequencing_report_service.repositiories.job_repo import JobRepository


@contextlib.contextmanager
def mock_job_repo():
    _mock_job_repo = mock.create_autospec(JobRepository, session_factory=None)
    _mock_job_repo.__enter__.return_value = _mock_job_repo

    def return_job_repo_factory():
        return _mock_job_repo

    yield _mock_job_repo, return_job_repo_factory
