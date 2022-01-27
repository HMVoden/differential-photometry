from pathlib import Path
import logging.config as lc
import logging
from typing import Optional, Tuple

from sqlalchemy.engine.base import Engine

from shutterbug.config.application import ApplicationConfig
import shutterbug.config as cf


def initialize_logging(
    config_file: Path = Path("./shutterbug.ini"), debug: bool = False
) -> None:
    """Loads all logging information from the target file

    :param config_file: File to load logging data from
    :param debug: Debug level override flag
    """

    lc.fileConfig(config_file)
    logging.debug("Initialized logging")
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.debug("Overriding logging level to debug")


def initialize_configuration(config_file: Optional[Path] = None) -> ApplicationConfig:

    """Loads Shutterbug configuration from file if present, otherwise loads default configuration

    :param file: Optional, filepath to the configuration file
    :returns: ApplicationConfig data object

    """
    if config_file is None:
        config_directory = cf.data_folder()
        config_file = config_directory / "shutterbug.ini"
        config = cf.from_file(config_file)
        if not config_file.exists():
            cf.to_file(config_file, config)
        return config
    else:
        if not config_file.exists():
            logging.error(
                f"Given configuration file {config_file.name} does not exist, falling back on default configuration"
            )
        return cf.from_file(config_file)


def initialize_database(db_path: Path) -> Engine:

    """Checks given path to see if database is present, if not creates entire path and database then returns engine object representing database

    :param db_path: Path to database
    :returns: SQLAlchemy engine object representing the database

    """
    pass


def initialize_application(
    config_file: Optional[Path] = None,
) -> Tuple[ApplicationConfig, Engine]:
    initialize_logging()
    config = initialize_configuration(config_file)
    db_path = config.data["database_path"]
    database = initialize_database(db_path)
    return config, database
