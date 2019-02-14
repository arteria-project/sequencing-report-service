# pylint: disable=W0223,W0221,W0511
# TODO: remove these exceptions, see DEVELOP-440
"""
Get the version of the service
"""
from arteria.web.handlers import BaseRestHandler

from sequencing_report_service import __version__ as version


class VersionHandler(BaseRestHandler):
    """
    Get the version of the service
    """

    def initialize(self, **kwargs):
        pass

    def get(self):
        """
        Returns the version of the checksum-service as json. Format looks as follows:
        {
           "version": "1.0.0"
        }
        """
        self.write_object({"version": version})
