
from arteria.web.handlers import BaseRestHandler

from sequencing_report_service.handlers import ACCEPTED, NOT_FOUND


class OneJobHandler(BaseRestHandler):
    """
    Handle checking status of jobs
    """

    def initialize(self, **kwargs):
        self.runner_service = kwargs['runner_service']

    def get(self, job_id):
        """
        TODO
        {
           "TODO": "TODO"
        }
        """
        job = self.runner_service.get_job(job_id)
        if job:
            job_as_dicts = job.to_dict()
            self.write_object(job_as_dicts)
        else:
            self.set_status(NOT_FOUND)


class ManyJobHandler(BaseRestHandler):

    def initialize(self, **kwargs):
        self.runner_service = kwargs['runner_service']

    def get(self):
        jobs = self.runner_service.get_jobs()
        jobs_as_dicts = list(map(lambda job: job.to_dict(), jobs))
        self.write_object({"jobs": jobs_as_dicts})


class JobStartHandler(BaseRestHandler):
    """
    Handle starting jobs
    """

    def initialize(self, **kwargs):
        self.runner_service = kwargs['runner_service']

    def post(self, runfolder):
        """
        TODO
        {
           "TODO": "TODO"
        }
        """
        job = self.runner_service.schedule(runfolder)
        self.set_status(status_code=ACCEPTED)
        self.write_object({'link': '{}://{}{}'.format(self.request.protocol,
                                                      self.request.host,
                                                      self.reverse_url('one_job', job.job_id))})
