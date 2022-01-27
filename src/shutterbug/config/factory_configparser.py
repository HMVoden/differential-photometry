import configparser
from pathlib import Path
from shutterbug.config.application import ApplicationConfig, default_config
from shutterbug.config.packages import DataConfig, PhotometryConfig, VariabilityConfig
import logging


def from_file(file: Path) -> ApplicationConfig:

    """Given a file, will generate an ApplicationConfig construct that contains all
    the configuration for the application that is present in the file. This
    generation will ignore all anomalous entries that the program does not
    understand and will only read entries that it does

    :param file: A path to a file
    :returns: ApplicationConfig object, containing all Shutterbug configuration in that file, if any

    """
    parser = configparser.ConfigParser()
    try:
        parser.read_file(str(file))
        return ApplicationConfig(
            _photometry=PhotometryConfig.fromconfigparser(parser),
            _variability=VariabilityConfig.fromconfigparser(parser),
            _data=DataConfig.fromconfigparser(parser),
        )
    except ValueError as e:
        logging.error(f"Failed to create application config with error {e}")
        return default_config


def to_file(file: Path, config: ApplicationConfig):
    pass
