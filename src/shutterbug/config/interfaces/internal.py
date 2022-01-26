from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any


class PackageConfigInterface(ABC):
    @property
    @abstractmethod
    def asdict(self) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def fromdict(cls, *args, **kwargs) -> PackageConfigInterface:
        raise NotImplementedError
