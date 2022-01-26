from pathlib import Path
from typing import Protocol
from abc import ABC, abstractmethod
from typing import Dict, Any


class Configuration(Protocol):
    def from_file(self, file: Path) -> ConfigurationInterface:
        ...

    def to_file(self, file: Path, config: ConfigurationInterface):
        ...
