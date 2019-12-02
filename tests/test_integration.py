import json
import codecs
import tempfile
from pathlib import Path
import os
import shutil

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from sequencing_report_service.app import configure_routes

from sequencing_report_service import __version__ as version


class TestIntegration(AsyncHTTPTestCase):

    db_file_path = None

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.db_file_path = Path(tempfile.NamedTemporaryFile().name)
        self.nextflow_log_dirs = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        if self.db_file_path.exists:
            os.remove(self.db_file_path.name)
        if os.path.exists(self.nextflow_log_dirs):
            shutil.rmtree(self.nextflow_log_dirs)

    def get_app(self):
        print(f'sqlite://{self.db_file_path.name}')
        config = {'db_connection_string': f'sqlite:///{self.db_file_path.name}',
                  'alembic_ini_path': 'config/alembic.ini',
                  'alembic_log_config_path': 'config/logger.config',
                  'alembic_scripts': './alembic/',
                  'process_queue_check_interval': 5,
                  'reports_dir': './tests/resources/reports',
                  'monitored_directories': ['./tests/resources/'],
                  'nextflow_log_dirs': self.nextflow_log_dirs,
                  'nextflow_config':
                  {'main_workflow_path': 'Molmed/summary-report-development',
                   'nf_config': 'config/nextflow.config',
                   'environment':
                   {'NXF_TEMP': '/tmp/'},
                   'parameters':
                   {'hello': '${DEFAULT:runfolder_path}'}}}
        app = Application(configure_routes(config))
        return app

    def test_get_version(self):
        response = self.fetch('/api/1.0/version')
        self.assertEqual(response.code, 200)
        self.assertEqual(json.loads(response.body), {'version': version})

    def test_start_job(self):
        response = self.fetch('/api/1.0/jobs/start/foo_runfolder', method='POST', body=json.dumps({}))
        self.assertEqual(response.code, 202)
        status_link = json.loads(response.body).get('link', None)
        self.assertTrue(status_link)
        status_response = self.fetch(status_link)
        self.assertTrue(json.loads(status_response.body).get('job_id'))
        self.assertTrue(json.loads(status_response.body).get('state'))

    def test_stop_job(self):
        # First start the job
        response = self.fetch('/api/1.0/jobs/start/foo_runfolder', method='POST', body=json.dumps({}))
        self.assertEqual(response.code, 202)
        status_link = json.loads(response.body).get('link', None)
        self.assertTrue(status_link)
        status_response = self.fetch(status_link)
        body_as_dict = json.loads(status_response.body)
        self.assertTrue(body_as_dict.get('job_id'))
        self.assertTrue(body_as_dict.get('state'))

        # Then stop it
        stop_response = self.fetch('/api/1.0/jobs/stop/{}'.format(body_as_dict['job_id']),
                                   method='POST',
                                   body=json.dumps({}))

        self.assertEqual(stop_response.code, 202)

        # And check its status
        status_after_stop_response = self.fetch(json.loads(stop_response.body)['link'])
        self.assertEqual(json.loads(status_after_stop_response.body)['state'], 'cancelled')

    def test_should_return_current_report(self):
        response = self.fetch('/reports/foo_runfolder/current/')
        self.assertEqual(response.code, 200)
        decoded_body = response.body.decode('UTF-8')
        self.assertIn('MultiQC', decoded_body)
        self.assertIn('VERSION2', decoded_body)

    def test_should_return_specific_report(self):
        response = self.fetch('/reports/foo_runfolder/v1/')
        self.assertEqual(response.code, 200)
        decoded_body = response.body.decode('UTF-8')
        self.assertIn('MultiQC', decoded_body)
        self.assertIn('VERSION1', decoded_body)

    def test_should_return_all_reports(self):
        response = self.fetch('/reports/foo_runfolder')
        self.assertEqual(response.code, 200)
        response_dict = json.loads(response.body)
        self.assertTrue(response_dict.get('links'))
        self.assertSetEqual(set(response_dict['links']),
                            set(['http://127.0.0.1:{}/reports/foo_runfolder/v1/'.format(self.get_http_port()),
                                 'http://127.0.0.1:{}/reports/foo_runfolder/current/'.format(self.get_http_port()),
                                 'http://127.0.0.1:{}/reports/foo_runfolder/v2/'.format(self.get_http_port())]))
