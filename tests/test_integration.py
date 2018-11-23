import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from sequencing_report_service.app import compose_application

from sequencing_report_service import __version__ as version


class TestIntegration(AsyncHTTPTestCase):
    def get_app(self):
        config = {}
        return Application(compose_application(config))

    def test_get_version(self):
        response = self.fetch('/api/1.0/version')
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {'version': version})

    def test_start_job(self):
        response = self.fetch('/api/1.0/jobs/start/foo', method='POST', body=json.dumps({}))
        self.assertEqual(response.code, 202)
        status_link = json.loads(response.body).get('link', None)
        self.assertTrue(status_link)
        status_response = self.fetch(status_link)
        self.assertTrue(json.loads(status_response.body).get('job_id'))
        self.assertTrue(json.loads(status_response.body).get('status'))
