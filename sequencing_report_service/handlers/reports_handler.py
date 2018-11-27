
import re
import logging

from tornado.web import StaticFileHandler, HTTPError

from sequencing_report_service.handlers import NOT_FOUND
from sequencing_report_service.exceptions import RunfolderNotFound

log = logging.getLogger(__name__)


class ReportHandler(StaticFileHandler):

    def initialize(self, path, reports_repo, default_filename=None, **kwargs):
        self.reports_repo = reports_repo
        super(ReportHandler, self).initialize(path, default_filename=default_filename)

    def validate_absolute_path(self, root, absolute_path):
        # This regex will match the following type of paths
        # <path_to_root>/reports/foo_runfolder
        # <path_to_root>/reports/foo_runfolder/v1
        # if there is a version this will be in the second group,
        # otherwise this will be empty.
        regex = r"^.+/" + re.escape(root) + r"/(\w+)/{0,1}(v\d+|)$"
        matches = re.match(regex, absolute_path)

        runfolder = matches.group(1)
        version = matches.group(2)

        if not runfolder:
            raise HTTPError(NOT_FOUND)

        try:
            if version:
                report_path = str(self.reports_repo.get_report_with_version(runfolder, version))
            else:
                report_path = str(self.reports_repo.get_current_report_for_runfolder(runfolder))
        except RunfolderNotFound:
            raise HTTPError(NOT_FOUND)

        return report_path
