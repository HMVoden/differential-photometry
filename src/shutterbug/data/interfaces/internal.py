from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generator, Set, Protocol
from shutterbug.data.star import Star
from pathlib import Path
import pandas as pd


class DataReaderInterface(ABC):
    @property
    @abstractmethod
    def all(self) -> Generator[pd.DataFrame, None, None]:
        raise NotImplementedError

    @abstractmethod
    def similar_to(self, star: str) -> pd.DataFrame:
        raise NotImplementedError


class DataWriterInterface(ABC):
    """Interface for data storage module, takes in a star or a group of stars and writes it to a storage medium for future reference"""

    @singledispatchmethod
    @abstractmethod
    def write(self, data: Star):
        raise NotImplementedError

    @write.register
    @abstractmethod
    def _(self, data: list):

        # have to use list as type due to bug with singledispatch
        raise NotImplementedError


class LoaderInterface(ABC):
    """Generic interface for an object that loads external star data from a source into memory"""

    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError


class FileLoaderFactory(Protocol):
    READABLE_TYPES: Set[str]

    def make_loader(self, file_path: Path) -> LoaderInterface:
        ...
