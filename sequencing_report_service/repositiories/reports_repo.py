"""
The ReportsRepository finds and presents reports.
"""
import os
from pathlib import Path
from sequencing_report_service.exceptions import RunfolderNotFound


class ReportsRepository:
    """
    The ReportsRepository finds and presents reports.
    There can be multiple reports associated with a single runfolder, these are denoted v1, v2, etc.
    There should be a link in the reports base directory which indicates which is the current report
    (normally this should be the most recent one).
    """

    def __init__(self, monitored_directories):
        """
        Instantiate a ReportsRepository
        :param monitored_directories: the base paths were runfolders/reports can be found.
        """
        self._monitored_directories = monitored_directories

    def _find_runfolder_dir(self, runfolder):
        for directory in self._monitored_directories:
            runfolder_path = Path(directory) / runfolder
            if runfolder_path.exists():
                return runfolder_path
        raise RunfolderNotFound

    def get_report_with_version(self, runfolder, version):
        """
        The path to the report for the specified version
        :param runfolder:
        :param version:
        :return: a Path to the report or None if there was no report
        :raises: RunfolderNotFound if there was no such runfolder
        """
        runfolder_dir = self._find_runfolder_dir(runfolder)
        return runfolder_dir / 'reports' / version / 'multiqc_report.html'

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

        runfolder_dir = self._find_runfolder_dir(runfolder)
        for report_dir in os.listdir(runfolder_dir / 'reports'):
            if os.path.isdir(runfolder_dir / 'reports' / report_dir):
                yield report_dir
