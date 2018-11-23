
import logging

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sequencing_report_service.models.db_models import Job, Status

log = logging.getLogger(__name__)


class JobRepository(object):

    def __init__(self, session_factory):
        self.session = session_factory()

    def add_job(self, runfolder):
        job = Job(runfolder=runfolder,
                  status=Status.PENDING)
        self.session.add(job)
        self.session.commit()
        return job

    def get_jobs(self):
        return self.session.query(Job).all()

    def get_job(self, job_id):
        return self.session.query(Job).filter(Job.job_id == job_id).one_or_none()

    def get_one_pending_job(self):
        return self.session.query(Job).filter(Job.status == Status.PENDING).first()

    def set_state_of_job(self, job_id, state):
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).one()
            job.status = state
            self.session.commit()
        except NoResultFound:
            log.error("Found no job with id: {}.".format(job_id))
        except MultipleResultsFound:
            log.error("Found multiple results with id: {}. Something is seriously "
                      "wrong in the database...".format(job_id))
        return False

    def set_pid_of_job(self, job_id, pid):
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).one()
            job.pid = pid
            self.session.commit()
        except NoResultFound:
            log.error("Found no job with id: {}.".format(job_id))
        except MultipleResultsFound:
            log.error("Found multiple results with id: {}. Something is seriously "
                      "wrong in the database...".format(job_id))
        return False
