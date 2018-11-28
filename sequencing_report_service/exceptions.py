

class SequencingReportBaseException(Exception):
    pass


class RunfolderNotFound(SequencingReportBaseException):
    pass


class UnableToStopJob(SequencingReportBaseException):
    pass
