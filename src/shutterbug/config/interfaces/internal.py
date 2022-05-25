from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class PackageConfig(ABC):
    @property
    @abstractmethod
    def asdict(self) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def fromdict(cls, *args, **kwargs) -> PackageConfig:
        raise NotImplementedError
