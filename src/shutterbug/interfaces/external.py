from abc import ABC, abstractmethod
from typing import Optional, Protocol
from pathlib import Path
from shutterbug.config.application import ApplicationConfig


class Initializer(Protocol):
    def initialize_logging(file: Path) -> None:
        ...

    def initialize_configuration(file: Optional[Path] = None) -> ApplicationConfig:
        ...
