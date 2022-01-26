from shutterbug.config.interfaces.internal import (
    AppConfigInterface,
    PackageConfigInterface,
)
from attr import field, define

from typing import Dict, Any


@define
class ApplicationConfig(AppConfigInterface):
    _main: PackageConfigInterface = field()
    _photometry: PackageConfigInterface = field()
    _variability: PackageConfigInterface = field()
    _data: PackageConfigInterface = field()

    def statistical_test(self, test: str) -> Dict[str, Any]:
        if test in self._variability.asdict.keys():
            return self._variability.asdict[test]
        else:
            raise ValueError(
                f"Attempted to find configuration for test {test}, configuration not found"
            )

    @property
    def data(self) -> Dict[str, Any]:
        return self._data.asdict

    @property
    def photometry(self) -> Dict[str, float]:
        return self._photometry.asdict
