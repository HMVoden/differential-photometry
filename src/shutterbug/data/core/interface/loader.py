from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator

from shutterbug.data.core.star import Star


class LoaderInterface(ABC):
    """Generic interface for an object that loads external star data from a source into memory"""

    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError


class FileLoaderInterface(LoaderInterface):
    """Interface for a loader that loads external star data from a file source into memory"""

    @classmethod
    @abstractmethod
    def is_readable(cls, input_file: Path) -> bool:
        raise NotImplementedError
