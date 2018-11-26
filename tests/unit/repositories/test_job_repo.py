

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pytest

from sequencing_report_service.models.db_models import SQLAlchemyBase, Status
from sequencing_report_service.repositiories.job_repo import JobRepository


class TestJobRepo(object):

    @pytest.fixture
    def db_session_factory(self):
        engine = create_engine('sqlite:///:memory:', echo=False)
        SQLAlchemyBase.metadata.create_all(engine)

        # Throw some data into the in-memory db
        session_factory = sessionmaker()
        session_factory.configure(bind=engine)
        return session_factory

    def test_add_job(self, db_session_factory):
        repo = JobRepository(db_session_factory)
        job = repo.add_job('foo_folder')
        assert job.runfolder == 'foo_folder'
        assert job.status == Status.PENDING

    def test_get_jobs(self, db_session_factory):
        repo = JobRepository(db_session_factory)
        repo.add_job('foo_folder')
        repo.add_job('bar_folder')
        jobs = repo.get_jobs()
        assert len(jobs) == 2
        assert list(map(lambda x: x.runfolder, jobs)) == ['foo_folder', 'bar_folder']

    def test_set_state_of_job(self, db_session_factory):
        repo = JobRepository(db_session_factory)
        repo.add_job('foo_folder')
        repo.set_state_of_job(1, Status.CANCELLED)
        assert repo.get_job(1).status == Status.CANCELLED

    def test_set_state_of_job(self, db_session_factory):
        repo = JobRepository(db_session_factory)
        assert repo.set_state_of_job(1111, Status.CANCELLED) is False

    def test_get_one_pending_job(self, db_session_factory):
        repo = JobRepository(db_session_factory)
        repo.add_job('foo_folder')
        repo.add_job('bar_folder')

        repo.set_state_of_job(1, Status.CANCELLED)
        job = repo.get_one_pending_job()

        assert job.job_id == 2

        repo.set_state_of_job(2, Status.READY)
        job_again = repo.get_one_pending_job()

        assert job_again is None