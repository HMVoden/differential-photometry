from shutterbug.config.interfaces.internal import (
    PackageConfigInterface,
)
from attr import field, define

from typing import Dict, Any

from shutterbug.config.packages import DataConfig, PhotometryConfig, VariabilityConfig


@define
class ApplicationConfig:
    _photometry: PackageConfigInterface = field()
    _variability: PackageConfigInterface = field()
    _data: PackageConfigInterface = field()

    @property
    def variability(self) -> Dict[str, Any]:
        return self._variability.asdict

    @property
    def data(self) -> Dict[str, Any]:
        return self._data.asdict

    @property
    def photometry(self) -> Dict[str, float]:
        return self._photometry.asdict


default_config = ApplicationConfig(
    _photometry=PhotometryConfig(), _variability=VariabilityConfig(), _data=DataConfig()
)
