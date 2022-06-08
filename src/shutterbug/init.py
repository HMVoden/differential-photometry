import logging
import logging.config as lc
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import shutterbug.config as cf
from shutterbug.config.application import ApplicationConfig


def initialize_logging(
    config_file: Path = Path("./shutterbug.ini"), debug: bool = False
) -> None:
    """Loads all logging information from the target file

    :param config_file: File to load logging data from
    :param debug: Debug level override flag
    """

    lc.fileConfig(config_file)
    logging.info("Initialized logging")
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.debug("Overriding logging level to debug")
    else:
        logger.setLevel(logging.INFO)


def initialize_configuration(config_file: Optional[Path] = None) -> ApplicationConfig:

    """Loads Shutterbug configuration from file if present, otherwise loads default configuration

    :param file: Optional, filepath to the configuration file
    :returns: ApplicationConfig data object

    """
    if config_file is None:
        logging.info("Initializing default configuration")
        config_directory = cf.data_folder()
        config_file = config_directory / "shutterbug.ini"
        config = cf.from_file(config_file)
        if not config_file.exists():
            cf.to_file(config_file, config)
        return config
    else:
        logging.info(f"Initializing configuration from file {config_file.name}")
        if not config_file.exists():
            logging.error(
                f"Given configuration file {config_file.name} does not exist, falling back on default configuration"
            )
        return cf.from_file(config_file)


def initialize_database(db_path: Path, db_url: str) -> Engine:

    """Checks given path to see if database is present, if not creates entire path and database then returns engine object representing database

    :param db_path: Path to database
    :returns: SQLAlchemy engine object representing the database

    """
    logging.info("Initializing database")
    if not db_path.exists():
        logging.info("Database not found, creating")
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch()
    engine = create_engine(db_url, future=True)
    _upgrade_db_to_latest(engine)
    return engine


def _upgrade_db_to_latest(engine: Engine):
    logging.info("Upgrading database to latest schema")
    cfg = Config("shutterbug.ini")
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "head")
