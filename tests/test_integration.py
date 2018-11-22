import json

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from sequencing_report_service.app import routes

from sequencing_report_service import __version__ as version


class TestIntegration(AsyncHTTPTestCase):
    def get_app(self):
        route_config = {}
        return Application(routes(**route_config))

    def test_homepage(self):
        response = self.fetch('/api/1.0/version')
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {'version': version})
