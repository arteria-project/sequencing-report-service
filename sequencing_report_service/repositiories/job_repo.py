"""
This module contains repository classes related to managing job objects.
"""

import logging

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from sequencing_report_service.models.db_models import Job, Status

log = logging.getLogger(__name__)


class JobRepository:
    """
    The JobRepository manages job objects. In this cases these are stored in the a database, but in principle
    they could be anywhere. It should be used as a context handler, i.e.:

        with JobRepository(db_session_factory) as job_repo:
            job_repo.add_job('foo_folder')

    This makes sure that the connection is closed correctly once the job_repo is no longer used.

    """

    def __init__(self, session_factory):
        """
        Create a new job repository
        :param session_factory: scoped_session object from sqlalchemy.
        """
        self.session_factory = session_factory

    def __enter__(self):
        """
        Handles setting up the context manager
        :return:
        """
        self.session = self.session_factory()
        return self

    def __exit__(self, *args):
        """
        Handlers shutting down the context manager
        :param args:
        :return:
        """
        self.session_factory.remove()

    def add_job(self, runfolder):
        """
        Add a new job for the specified runfolder. The state of the job will be set as pending.
        :param runfolder: to start job for
        :return: the created Job
        """
        job = Job(runfolder=runfolder,
                  status=Status.PENDING)
        self.session.add(job)
        self.session.commit()
        return job

    def get_jobs(self):
        """
        Get all jobs
        :return: all the Jobs in the database, None if none found
        """
        return self.session.query(Job).all()

    def get_jobs_with_status(self, status):
        """
        Get all jobs with specified status
        :param status:
        :return: all the jobs, or None
        """
        return self.session.query(Job).filter(Job.status == status).all()

    def get_job(self, job_id):
        """
        Get the job with the specified job_id
        :param job_id:
        :return: a Job, or None if it does not exist
        """
        return self.session.query(Job).filter(Job.job_id == job_id).one_or_none()

    def get_one_pending_job(self):
        """
        Get the first available pending Job
        :return: A pending job or none.
        """
        return self.session.query(Job).filter(Job.status == Status.PENDING).first()

    def expunge_object(self, obj):
        """
        This will remove the object from the current session. This is necessary if you
        want to pass the object on. However, please note that after this point no
        changes made to the object will be persisted.
        :param obj: to remove from current session.
        :return: None
        """
        if obj:
            self.session.expunge(obj)

    def set_state_of_job(self, job_id, state):
        """
        Set the state of the of the specified job to the specified state
        :param job_id: of Job to change
        :param state: Instance of sequencing_report_models.db_models.Status
        :return: The job which status was changed, or none if no (or multiple) jobs with id were found.
        """
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).one()
            job.status = state
            self.session.commit()
            return job
        except NoResultFound:
            log.error("Found no job with id: %s.", job_id)
        except MultipleResultsFound as error:
            log.error("Found multiple results with id: %s. Something is seriously "
                      "wrong in the database...", job_id)
            raise error
        return None

    def set_pid_of_job(self, job_id, pid):
        """
        Sets the process id associated with a specific job
        :param job_id: to change pid of
        :param pid: to set
        :return: the Job changed or None if no job was found
        """
        try:
            job = self.session.query(Job).filter(Job.job_id == job_id).one()
            job.pid = pid
            self.session.commit()
            return Job
        except NoResultFound:
            log.error("Found no job with id: %s.", job_id)
        except MultipleResultsFound as error:
            log.error("Found multiple results with id: %s. Something is seriously "
                      "wrong in the database...", job_id)
            raise error
        return None

    def clear_out_stale_jobs_at_startup(self):
        """
        This method will set all jobs which have status started, i.e. jobs which
        should be running, but are not when the service is started. Should only be
        called once at the start up of the application
        :param job_repo_factory
        :return:
        """
        stale_jobs = self.get_jobs_with_status(Status.STARTED)
        for job in stale_jobs:
            log.info("Setting status of job with id=%s, to %s because it was stale.", job.job_id, Status.CANCELLED)
            self.set_state_of_job(job_id=job.job_id, state=Status.CANCELLED)
