
import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

import mock

from sequencing_report_service.app import routes
from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.models.db_models import Job, Status


class TestJobHandler(AsyncHTTPTestCase):
    def get_app(self):

        mock_runner_service = mock.create_autospec(LocalRunnerService)
        job = Job(job_id=1, runfolder='foo', status=Status.PENDING)
        mock_runner_service.get_jobs = mock.MagicMock(return_value=[job])
        mock_runner_service.get_job = mock.MagicMock(return_value=job)
        mock_runner_service.schedule = mock.MagicMock(return_value=job)
        mock_runner_service.stop = mock.MagicMock(return_value=job)

        return Application(routes(runner_service=mock_runner_service))

    def test_get_jobs(self):
        response = self.fetch('/api/1.0/jobs/')
        self.assertEqual(response.code, 200)
        resp_dict = json.loads(response.body)['jobs'][0]
        self.assertEqual(resp_dict['runfolder'], 'foo')
        self.assertEqual(resp_dict['job_id'], 1)
        self.assertEqual(resp_dict['status'], 'pending')

    def test_get_job(self):
        response = self.fetch('/api/1.0/jobs/1')
        self.assertEqual(response.code, 200)
        resp_dict = json.loads(response.body)
        self.assertEqual(resp_dict['runfolder'], 'foo')
        self.assertEqual(resp_dict['job_id'], 1)
        self.assertEqual(resp_dict['status'], 'pending')

    def test_start_job(self):
        response = self.fetch('/api/1.0/jobs/start/foo', method='POST', body=json.dumps({}))
        self.assertEqual(response.code, 202)
        self.assertDictEqual(json.loads(response.body),
                             {'link':
                              'http://127.0.0.1:{}/api/1.0/jobs/{}'.format(self.get_http_port(), 1)})

    def test_stop_job(self):
        response = self.fetch('/api/1.0/jobs/stop/1', method='POST', body=json.dumps({}))
        self.assertEqual(response.code, 202)
        self.assertDictEqual(json.loads(response.body),
                             {'link': 'http://127.0.0.1:{}/api/1.0/jobs/{}'.format(self.get_http_port(), 1)})
