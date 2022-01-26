from abc import ABC, abstractmethod
from typing import Dict, Any
from __future__ import annotations


class AppConfigInterface(ABC):
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


class PackageConfigInterface(ABC):
    @property
    @abstractmethod
    def dict(self) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def fromdict(cls, *args, **kwargs) -> PackageConfigInterface:
        raise NotImplementedError
