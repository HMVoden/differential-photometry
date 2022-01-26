from pathlib import Path
from typing import Protocol

from shutterbug.config.application import ApplicationConfig


class ConfigurationFactory(Protocol):
    def from_file(self, file: Path) -> ApplicationConfig:
        ...

    def to_file(self, file: Path, config: ApplicationConfig):
        ...
