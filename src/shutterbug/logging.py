from pathlib import Path
import logging.config as lc
import logging


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
