
from pathlib import Path

from sequencing_report_service.exceptions import RunfolderNotFound


class ReportsRepository(object):

    def __init__(self, reports_search_path):
        self._reports_search_path = reports_search_path

    def get_report_with_version(self, runfolder, version):
        report_path = Path(self._reports_search_path) / runfolder / 'reports' / version / 'multiqc_report.html'
        if report_path.exists():
            return report_path
        else:
            raise RunfolderNotFound

    def get_current_report_for_runfolder(self, runfolder):
        return self.get_report_with_version(runfolder, 'current')
