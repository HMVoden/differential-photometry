import configparser
from pathlib import Path
from attr import define, field
import logging.config as lc
import logging

from shutterbug.interfaces.internal import ConfigurationInterface


def initialize_logging(
    config_file: Path = Path("./shutterbug.ini"), debug: bool = False
):
    # sanity check
    lc.fileConfig(config_file)
    logging.debug("Initialized logging")
    logger = logging.getLogger()
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.debug("Overriding logging level to debug")


@define
class ApplicationConfig(ConfigurationInterface):
    ...
