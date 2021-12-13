from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator

from shutterbug.data.core.star import Star

class LoaderInterface(ABC):
    """Generic interface for an object that loads star data from a source"""
    def __iter__() -> Generator[Star, None, None]:
        raise NotImplementedError

    def __len__() -> int:
        raise NotImplementedError


class FileLoaderInterface(LoaderInterface, ABC):
    """Interface for a loader that loads star data from a file source"""
    @abstractmethod
    @classmethod
    def is_readable(cls, input_file: Path) -> bool:
        raise NotImplementedError
