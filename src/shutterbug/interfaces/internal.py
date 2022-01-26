from pathlib import Path
from typing import Protocol
from abc import ABC, abstractmethod
from typing import Dict, Any

from shutterbug.config.application import ApplicationConfig


class Configuration(Protocol):
    def from_file(self, file: Path) -> ApplicationConfig:
        ...

    def to_file(self, file: Path, config: ApplicationConfig):
        ...
