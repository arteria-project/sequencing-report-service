# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from alembic.config import Config as AlembicConfig
from alembic.command import upgrade as upgrade_db

from tornado.web import URLSpec as url
from tornado.ioloop import PeriodicCallback

from arteria.web.app import AppService

from sequencing_report_service.handlers.version_handler import VersionHandler
from sequencing_report_service.handlers.job_handler import OneJobHandler, ManyJobHandler, JobStartHandler
from sequencing_report_service.services.local_runner_service import LocalRunnerService
from sequencing_report_service.repositiories.job_repo import JobRepository

log = logging.getLogger(__name__)


def routes(**kwargs):
    """
    Setup routes and feed them any kwargs passed, e.g.`routes(config=app_svc.config_svc)`
    Help will be automatically available at /api, and will be based on the
    doc strings of the get/post/put/delete methods
    :param: **kwargs will be passed when initializing the routes.
    """
    return [
        url(r"/api/1.0/version", VersionHandler, name="version", kwargs=kwargs),
        url(r"/api/1.0/jobs/start/(?!.*\/)(.*)$", JobStartHandler, name="job_start", kwargs=kwargs),
        url(r"/api/1.0/jobs/(\d+)$", OneJobHandler, name="one_job", kwargs=kwargs),
        url(r"/api/1.0/jobs/$", ManyJobHandler, name="many_jobs", kwargs=kwargs)
    ]


def create_and_migrate_db(db_engine):
    """
    Configures alembic and runs any none applied migrations found in the
    `scripts_location` folder.
    :param db_engine: engine handle for the database to apply the migrations to
    :return: None
    """
    alembic_cfg = AlembicConfig(file_='config/alembic.ini')
    alembic_cfg.set_section_option("alembic", "log_config_file", "config/logger.config")

    with db_engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        upgrade_db(alembic_cfg, "head")


def compose_application(config):

    connection_string = 'sqlite:///sequencing_reports.db'
    engine = create_engine(connection_string, echo=False)

    # Instantiate db, services, and repos
    log.info("Creating DB migrations")
    create_and_migrate_db(engine)

    log.info("Setup connection to db")
    session_factory = scoped_session(sessionmaker())
    session_factory.configure(bind=engine)

    job_repo = JobRepository(session_factory)
    local_runner_service = LocalRunnerService(job_repo)

    PeriodicCallback(local_runner_service.process_job_queue, 10*1000).start()
    return routes(config=config,
                  runner_service=local_runner_service)


def start(package=__package__):
    """
    Start the app
    """
    app_svc = AppService.create(package)
    config = app_svc.config_svc
    app_svc.start(compose_application(config))
