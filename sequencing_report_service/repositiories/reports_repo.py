
import os
from pathlib import Path
import logging

from sequencing_report_service.exceptions import RunfolderNotFound

log = logging.getLogger(__name__)


class ReportsRepository(object):
    """
    The ReportsRepository finds and presents reports.
    There can be multiple reports associated with a single runfolder, these are denoted v1, v2, etc.
    There should be a link in the reports base directory which indicates which is the current report
    (normally this should be the most recent one).
    """

    def __init__(self, reports_search_path):
        """
        Instantiate a ReportsRepository
        :param reports_search_path: the base paths were reports can be found.
        """
        self._reports_search_path = reports_search_path

    def get_report_with_version(self, runfolder, version):
        """
        The path to the report for the specified version
        :param runfolder:
        :param version:
        :return: a Path to the report or None if there was no report
        :raises: RunfolderNotFound if there was no such runfolder
        """
        runfolder_path = Path(self._reports_search_path) / runfolder
        if not runfolder_path.exists():
            raise RunfolderNotFound

        report_path = runfolder_path / 'reports' / version / 'multiqc_report.html'
        if report_path.exists():
            return report_path
        else:
            return None

    def get_current_report_for_runfolder(self, runfolder):
        """
        Get the current report for the runfolder.
        :param runfolder:
        :return: the path to the report or None
        :raises: RunfolderNotFound if there was no such runfolder
        """
        return self.get_report_with_version(runfolder, 'current')

    def get_all_report_versions_for_runfolder(self, runfolder):
        """
        Find all the report versions for the specified runfolder
        :param runfolder:
        :return: a generator of available version, e.g. v1, v2, current
        """
        reports_path = Path(self._reports_search_path) / runfolder / 'reports'

        if not reports_path.exists():
            raise RunfolderNotFound

        for report_dir in os.listdir(reports_path):
            if os.path.isdir(reports_path / report_dir):
                yield report_dir
