import logging
import logging.config
from typing import Dict


def initialize_logging(
    version: int, enabled: bool, formatters: Dict, handlers: Dict, root: Dict
):
    if enabled == True:
        log_dict = {
            "version": version,
            "formatters": formatters,
            "handlers": handlers,
            "root": root,
        }
        logging.config.dictConfig(log_dict)
        logging.debug("Logging configured")
