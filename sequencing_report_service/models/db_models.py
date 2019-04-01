# pylint: disable=C0103

"""
Use this as the base for all database based models. This is used by alembic to know what the tables
should look like in the database, so defining new base classes elsewhere will mean that they will not
be updated properly in the actual database.
"""
import enum as base_enum

from sqlalchemy import Column, Integer, String, Enum, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from arteria.web.state import State

SQLAlchemyBase = declarative_base()


class Status(base_enum.Enum):
    """
    Possible states of a job
    """
    # This is an ugly hack since the Arteria state class is not
    # an Enum because the it is not supported in Python2.
    # /JD 2018-11-23
    NONE = State.NONE
    PENDING = State.PENDING
    READY = State.READY
    STARTED = State.STARTED
    DONE = State.DONE
    ERROR = State.ERROR
    CANCELLED = State.CANCELLED


class Job(SQLAlchemyBase):
    """
    This table contains information about jobs that we have run.
    """
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    runfolder = Column(String, nullable=False)
    pid = Column(Integer, nullable=True)
    status = Column(Enum(Status))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    log = Column(Text(convert_unicode=True), nullable=True)

    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        """
        Converts object to dict
        """
        return {'job_id': self.job_id,
                'runfolder': self.runfolder,
                'pid': self.pid if self.pid else '',
                'status': self.status.value,
                'created': str(self.time_created),
                'updated': str(self.time_updated),
                'log': str(self.log) if self.log else ''}
