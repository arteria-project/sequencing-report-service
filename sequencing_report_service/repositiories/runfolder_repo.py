
from pathlib import Path

from sequencing_report_service.exceptions import ConfigurationError, RunfolderNotFound


class RunfolderRepository():

    def __init__(self, monitored_directories):
        self._monitoried_dirs = monitored_directories
        if not isinstance(self._monitoried_dirs, list):
            raise ConfigurationError('"monitored_directories" in the config must be a list!')

    def get_runfolder(self, runfolder):
        for d in self._monitoried_dirs:
            potential_runfolder = Path(d) / runfolder
            if potential_runfolder.exists():
                return potential_runfolder
        raise RunfolderNotFound(
            f"Could not identify a runfolder with the name: ${runfolder} in any of the monitored directories.")
