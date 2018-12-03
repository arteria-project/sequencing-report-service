

class SequencingReportBaseException(Exception):
    pass


class ConfigurationError(SequencingReportBaseException):
    pass


class RunfolderNotFound(SequencingReportBaseException):
    pass


class UnableToStopJob(SequencingReportBaseException):
    pass
