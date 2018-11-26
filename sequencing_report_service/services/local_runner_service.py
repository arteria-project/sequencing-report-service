
import logging
import subprocess
import os
import signal

from sequencing_report_service.models.db_models import Status

log = logging.getLogger(__name__)


class RunningJob(object):
    def __init__(self, job, process):
        self.job = job
        self.process = process


class LocalRunnerService(object):

    def __init__(self, job_repo):
        self._job_repo = job_repo
        self._currently_running_job = None

    def _start_process(self, job):
        # TODO Replace with starting actual nextflow job
        process = subprocess.Popen(['sleep', '1'])

        self._currently_running_job = RunningJob(job, process)
        self._job_repo.set_state_of_job(job_id=job.job_id, state=Status.STARTED)
        self._job_repo.set_pid_of_job(job.job_id, process.pid)

    def _update_process_status(self):
        log.debug("Updating status of processes...")
        return_code = self._currently_running_job.process.poll()
        command = ' '.join(self._currently_running_job.process.args)
        # It looks a bit backwards to check for 'is not None' here. The reason for doing it this way
        # is that poll will return None, or the exit status, but since 0 evaluates to False, we need to
        # check specifically for not being None here before continuing. /JD 2018-11-26
        if return_code is not None:
            if return_code == 0:
                log.info("Successfully completed process: {}".format(command))
                self._job_repo.set_state_of_job(self._currently_running_job.job.job_id,
                                                Status.DONE)
                self._currently_running_job = None
            else:
                log.error("Found non-zero exit code: {} for command: {}".format(return_code, command))
                self._job_repo.set_state_of_job(self._currently_running_job.job.job_id,
                                                Status.ERROR)
                self._currently_running_job = None
        else:
            log.debug("Found no return code for process: {}. Will keep polling later".format(command))

    def stop(self, job_id):
        job = self._job_repo.get_job(job_id)
        if job and job.status == Status.PENDING:
            log.info("Found pending job: {}. Will set its status to cancelled.".format(job))
            self._job_repo.set_state_of_job(job_id, Status.CANCELLED)
            return job
        if job and job.status == Status.STARTED:
            log.info("Will stop the currently running job.")
            current_pid = self._currently_running_job.process.pid
            os.kill(current_pid, signal.SIGTERM)
            self._job_repo.set_state_of_job(job_id, Status.CANCELLED)
            self._currently_running_job = None
            return job
        else:
            log.debug("Found no job to cancel with with job id: {}. Or it was not in a cancellable state.")
            return job

    def schedule(self, runfolder):
        return self._job_repo.add_job(runfolder=runfolder)

    def get_jobs(self):
        return self._job_repo.get_jobs()

    def get_job(self, job_id):
        return self._job_repo.get_job(job_id)

    def process_job_queue(self):
        log.debug("Processing job queue.")
        if self._currently_running_job:
            self._update_process_status()
        else:
            job = self._job_repo.get_one_pending_job()
            if job:
                log.debug("Found pending job. Will start it.")
                self._start_process(job)
            else:
                log.debug("No pending jobs found.")
