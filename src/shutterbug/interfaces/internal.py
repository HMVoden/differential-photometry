from pathlib import Path
from typing import Protocol
from abc import ABC, abstractmethod
from typing import Dict, Any


class ConfigurationInterface(ABC):
    @abstractmethod
    def statistical_test(self, test: str) -> Dict[str, Any]:
        raise NotImplementedError

    @property
    @abstractmethod
    def photometry(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def data(self) -> Dict[str, Any]:
        raise NotImplementedError


class ConfigurationManager(Protocol):
    def from_file(self, file: Path) -> ConfigurationInterface:
        ...

    def to_file(self, file: Path, config: ConfigurationInterface):
        ...
