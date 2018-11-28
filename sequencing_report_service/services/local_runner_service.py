
import logging
import subprocess
import os
import signal

from sequencing_report_service.models.db_models import Status
from sequencing_report_service.exceptions import UnableToStopJob

log = logging.getLogger(__name__)


class RunningJob(object):
    def __init__(self, job_id, process):
        self.job_id = job_id
        self.process = process


class LocalRunnerService(object):

    def __init__(self, job_repo_factory):
        self._job_repo_factory = job_repo_factory
        self._currently_running_job = None

    def _start_process(self, job):
        with self._job_repo_factory() as job_repo:
            # TODO Replace with starting actual nextflow job
            process = subprocess.Popen(['sleep', '1'])

            self._currently_running_job = RunningJob(job.job_id, process)
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
                if return_code == 0:
                    log.info("Successfully completed process: {}".format(command))
                    job_repo.set_state_of_job(self._currently_running_job.job_id,
                                              Status.DONE)
                    self._currently_running_job = None
                else:
                    log.error("Found non-zero exit code: {} for command: {}".format(return_code, command))
                    job_repo.set_state_of_job(self._currently_running_job.job_id,
                                              Status.ERROR)
                    self._currently_running_job = None
            else:
                log.debug("Found no return code for process: {}. Will keep polling later".format(command))

    def stop(self, job_id):
        with self._job_repo_factory() as job_repo:
            job = job_repo.get_job(job_id)
            if job and job.status == Status.PENDING:
                log.info("Found pending job: {}. Will set its status to cancelled.".format(job))
                job_repo.set_state_of_job(job_id, Status.CANCELLED)
                return job
            if job and job.status == Status.STARTED:
                log.info("Will stop the currently running job.")
                current_pid = self._currently_running_job.process.pid
                os.kill(current_pid, signal.SIGTERM)
                job_repo.set_state_of_job(job_id, Status.CANCELLED)
                self._currently_running_job = None
                return job
            else:
                log.debug("Found no job to cancel with with job id: {}. Or it was not in a cancellable state.")
                raise UnableToStopJob()

    def schedule(self, runfolder):
        with self._job_repo_factory() as job_repo:
            return job_repo.add_job(runfolder=runfolder).job_id

    def get_jobs(self):
        with self._job_repo_factory() as job_repo:
            return job_repo.get_jobs()

    def get_job(self, job_id):
        with self._job_repo_factory() as job_repo:
            return job_repo.get_job(job_id)

    def process_job_queue(self):
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
