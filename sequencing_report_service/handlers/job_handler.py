
from tornado.web import HTTPError

from arteria.web.handlers import BaseRestHandler

from sequencing_report_service.handlers import ACCEPTED, NOT_FOUND, FORBIDDEN
from sequencing_report_service.exceptions import UnableToStopJob

class OneJobHandler(BaseRestHandler):
    """
    Handle checking status of jobs. Will return a representation of a job as json e.g.:
        {"job_id": 1, "runfolder": "foo", "pid": 3837, "status": "done",
        "created": "2018-11-27 12:06:26", "updated": "2018-11-27 12:06:44"}
    """

    def initialize(self, runner_service, **kwargs):
        self.runner_service = runner_service

    def get(self, job_id):
        """
        Will return the job object corresponding to a specific job id. It will return or the form:
        {"job_id": 1, "runfolder": "foo", "pid": 3837, "status": "done",
         "created": "2018-11-27 12:06:26", "updated": "2018-11-27 12:06:44"}
        """
        job = self.runner_service.get_job(job_id)
        if job:
            job_as_dicts = job.to_dict()
            self.write_object(job_as_dicts)
        else:
            raise HTTPError(NOT_FOUND)


class ManyJobHandler(BaseRestHandler):
    """
    Handles checking the status of jobs.
    TODO Add the option of filtering the jobs returned, e.g. for status
    Returns a json object on the following format:
    {
    "jobs": [
        {
            "created": "2018-11-27 12:06:26",
            "job_id": 1,
            "pid": 3837,
            "runfolder": "foo",
            "status": "done",
            "updated": "2018-11-27 12:06:44"
        },
        {
            "created": "2018-11-27 12:09:59",
            "job_id": 2,
            "pid": 4394,
            "runfolder": "foo",
            "status": "done",
            "updated": "2018-11-27 12:11:11"
        }
        ]
    }
    """

    def initialize(self, runner_service, **kwargs):
        self.runner_service = runner_service

    def get(self):
        """
        Will return the status of all jobs (or fewer depending on filter). The return json has the format:

        {
        "jobs": [
            {
                "created": "2018-11-27 12:06:26",
                "job_id": 1,
                "pid": 3837,
                "runfolder": "foo",
                "status": "done",
                "updated": "2018-11-27 12:06:44"
            },
            {
                "created": "2018-11-27 12:09:59",
                "job_id": 2,
                "pid": 4394,
                "runfolder": "foo",
                "status": "done",
                "updated": "2018-11-27 12:11:11"
            }
            ]
        }
        """
        jobs = self.runner_service.get_jobs()
        jobs_as_dicts = list(map(lambda job: job.to_dict(), jobs))
        self.write_object({"jobs": jobs_as_dicts})


class JobStartHandler(BaseRestHandler):
    """
    Handle starting jobs. Please note that any jobs started will simply be scheduled to run
    and that it will not be run until there is capacity in the runner to add more jobs.
    """

    def initialize(self, runner_service, **kwargs):
        self.runner_service = runner_service

    def post(self, runfolder):
        """
        Posting to this endpoint will start a job for the provided runfolder, e.g.:
            curl -X POST -w'\n' localhost:9999/api/1.0/jobs/start/foo
        The endpoint will then return a link where the run can be monitored:
            {"link": "http://localhost:9999/api/1.0/jobs/130"}
        """
        #TODO Check that runfolder exists before starting
        job = self.runner_service.schedule(runfolder)
        self.set_status(status_code=ACCEPTED)
        self.write_object({'link': '{}://{}{}'.format(self.request.protocol,
                                                      self.request.host,
                                                      self.reverse_url('one_job', job.job_id))})


class JobStopHandler(BaseRestHandler):
    """
    Handle stopping jobs. This will stops jobs which are eligible for stopping, i.e. jobs which have pending or
    started as their status.
    """

    def initialize(self, **kwargs):
        self.runner_service = kwargs['runner_service']

    def post(self, job_id):
        """
        curl -X POST -w'\n' localhost:9999/api/1.0/jobs/stop/1
        Will return an endpoint at which the status of the job can be checked on the format:
            {"link": "http://localhost:9999/api/1.0/jobs/1"}
        If it was possible to stop the job the status code will be 202 (ACCEPTED), and if it was not
        possible to stop the job it will be 403 (FORBIDDEN). If there was no corresponding job_id, the
        status code will be 404 (NOT_FOUND)
        """
        if not self.runner_service.get_job(job_id):
            raise HTTPError(NOT_FOUND)

        try:
            self.runner_service.stop(job_id)
            self.set_status(status_code=ACCEPTED)
        except UnableToStopJob:
            self.set_status(status_code=FORBIDDEN)

        self.write_object({'link': '{}://{}{}'.format(self.request.protocol,
                                                      self.request.host,
                                                      self.reverse_url('one_job', job_id))})
