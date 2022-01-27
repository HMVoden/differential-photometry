from shutterbug.config.interfaces.internal import (
    PackageConfigInterface,
)
from attr import field, define
from pathlib import Path
from typing import Dict, Any
import logging
from shutterbug.config.packages import DataConfig, PhotometryConfig


@define
class ApplicationConfig:
    _photometry: PackageConfigInterface = field()
    _data: PackageConfigInterface = field()

    @property
    def data(self) -> Dict[str, Any]:
        return self._data.asdict

    @property
    def photometry(self) -> Dict[str, float]:
        return self._photometry.asdict

    @property
    def all(self) -> Dict[str, Any]:
        return {
            "photometry": self.photometry,
            "data": self.data,
        }


def make_data_folder(folder: Path = Path.home() / ".shutterbug") -> Path:

    """Creates and returns the data folder that the database and configuration
    resides in

        :param folder: Target data folder, optional. Default: <user home>/.shutterbug
        :returns: Path to the data folder

    """
    if not folder.exists():
        try:
            logging.debug(f"Folder {make_data_folder} does not exist, creating")
            folder.mkdir(parents=True)
        except IOError as e:
            logging.error(f"Unable to create data folder, received error {e}")
    return folder


default_config = ApplicationConfig(
    photometry=PhotometryConfig(),
    data=DataConfig(),  # type:ignore
)
