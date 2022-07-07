import logging
from pathlib import Path
from typing import Any, Dict

from attr import define, field
from shutterbug.config.interfaces.internal import PackageConfig
from shutterbug.config.packages import DataConfig, PhotometryConfig, VariabilityConfig


@define
class ApplicationConfig:
    _photometry: PhotometryConfig = field()
    _data: DataConfig = field()
    _variability: VariabilityConfig = field()

    @property
    def data(self) -> DataConfig:
        return self._data

    @property
    def photometry(self) -> PhotometryConfig:
        return self._photometry

    @property
    def variability(self) -> VariabilityConfig:
        return self._variability

    @property
    def all(self) -> Dict[str, Any]:
        return {
            "photometry": self.photometry,
            "data": self.data,
            "variability": self.variability,
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
    photometry=PhotometryConfig(),  # type: ignore
    data=DataConfig(),  # type: ignore
    variability=VariabilityConfig(),  # type: ignore
)
