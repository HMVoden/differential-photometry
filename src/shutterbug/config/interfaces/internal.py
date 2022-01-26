from abc import ABC, abstractmethod
from typing import Dict, Any
from __future__ import annotations


class PackageConfigInterface(ABC):
    @property
    @abstractmethod
    def asdict(self) -> Dict:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def fromdict(cls, *args, **kwargs) -> PackageConfigInterface:
        raise NotImplementedError
