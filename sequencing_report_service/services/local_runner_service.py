# pylint: disable=R0903,W0511
# Intentionally disabling R0903 too-few-public-methods error to allow for _RunningJob
# W0511-fixme pending DEVELOP-237
"""
Contains classes to run and manage jobs.
"""

import logging
import subprocess
import os
import signal

from sequencing_report_service.models.db_models import Status
from sequencing_report_service.exceptions import UnableToStopJob

log = logging.getLogger(__name__)


class _RunningJob:
    """
    Small class to hold information about the currently running job.
    """

    def __init__(self, job_id, process):
        self.job_id = job_id
        self.process = process


class LocalRunnerService:
    """
    The local runner service will start jobs one by one and attempt to run to the command associated with
    it. In order for jobs to actually be started `process_job_queue` must be called. This can e.g. be done
    periodically from the application event loop.

    Please note that while the LocalRunnerService will use Job instances returned from the JobRepository,
    these should not be returned to the called of LocalRunnerService. The reason for that is that they will
    have lost their database session, which will cause errors. So in general return the job id (or what ever
    information is useful) of the job if you need to process it in some other way downstream rather than
    returning the job instance.
    """

    def __init__(self, job_repo_factory, nextflow_command_generator):
        """
        Create a new instance of LocalRunnerService
        :param: job_repo_factory factory method which can produce new JobRepository instances
        :param: nextflow_command_generator used to generate nf commands
        """
        self._job_repo_factory = job_repo_factory
        self._nextflow_jobs_factory = nextflow_command_generator
        self._currently_running_job = None

    def _start_process(self, job):
        with self._job_repo_factory() as job_repo:
            log.debug("Will start command: %s", job.command)
            process = subprocess.Popen(job.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            self._currently_running_job = _RunningJob(job.job_id, process)
            job_repo.set_state_of_job(job_id=job.job_id, state=Status.STARTED)
            job_repo.set_pid_of_job(job.job_id, process.pid)

    def _update_process_status(self):
        with self._job_repo_factory() as job_repo:
            log.debug("Updating status of processes...")
            return_code = self._currently_running_job.process.poll()
            command = ' '.join(self._currently_running_job.process.args)
            # It looks a bit backwards to check for 'is not None' here. The reason for doing it this way
            # is that poll will return None, or the exit status, but since 0 evaluates to False, we need to
            # check specifically for not being None here before continuing. /JD 2018-11-26
            if return_code is not None:
                cmd_log = self._currently_running_job.process.stdout.read().decode('UTF-8')

                if return_code == 0:
                    log.info("Successfully completed process: %s", command)
                    job_repo.set_state_of_job(job_id=self._currently_running_job.job_id,
                                              state=Status.DONE,
                                              cmd_log=cmd_log)
                    self._currently_running_job = None
                else:
                    log.error("Found non-zero exit code: %s for command: %s", return_code, command)
                    job_repo.set_state_of_job(job_id=self._currently_running_job.job_id,
                                              state=Status.ERROR,
                                              cmd_log=cmd_log)
                    self._currently_running_job = None
            else:
                log.debug("Found process: %s appears to still be running. Will keep polling later.", command)

    def stop(self, job_id):
        """
        Stop the job with the specified id
        :param job_id:
        :return: the job id of the job that was stopped.
        """
        with self._job_repo_factory() as job_repo:
            job = job_repo.get_job(job_id)
            if job and job.status == Status.PENDING:
                log.info("Found pending job: %s. Will set its status to cancelled.", job)
                job_repo.set_state_of_job(job_id, Status.CANCELLED)
                return job.job_id
            if job and job.status == Status.STARTED:
                log.info("Will stop the currently running job.")
                current_pid = self._currently_running_job.process.pid
                os.kill(current_pid, signal.SIGTERM)
                job_repo.set_state_of_job(job_id, Status.CANCELLED)
                self._currently_running_job = None
                return job.job_id
            log.debug("Found no job to cancel with with job id: {}. Or it was not in a cancellable state.")
            raise UnableToStopJob()

    def schedule(self, runfolder):
        """
        Schedule a new job for the specified runfolder
        :param runfolder:
        :return: the job id of the started job
        """
        with self._job_repo_factory() as job_repo:
            nf_cmd = self._nextflow_jobs_factory.command(runfolder)
            return job_repo.add_job(command=nf_cmd).job_id

    def get_jobs(self):
        """
        Return all jobs as a list
        :return: list of all jobs
        """
        with self._job_repo_factory() as job_repo:
            for job in job_repo.get_jobs():
                job_repo.expunge_object(job)
            return job_repo.get_jobs()

    def get_job(self, job_id):
        """
        Get the job corresponding to the specific job id
        :param job_id: to fetch job for.
        :return: a Job, or None if there is no job with the specified job id
        """
        with self._job_repo_factory() as job_repo:
            job = job_repo.get_job(job_id)
            job_repo.expunge_object(job)
            return job

    def process_job_queue(self):
        """
        Process the current job queue, starting any jobs which are eligible for starting.
        This method needs to be called periodically in order for jobs to actually be processed.
        :return: None
        """
        with self._job_repo_factory() as job_repo:
            log.debug("Processing job queue.")
            if self._currently_running_job:
                self._update_process_status()
            else:
                job = job_repo.get_one_pending_job()
                if job:
                    log.debug("Found pending job. Will start it.")
                    self._start_process(job)
                else:
                    log.debug("No pending jobs found.")
