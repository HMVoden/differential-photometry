from __future__ import annotations
from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generator
from shutterbug.data.star import Star
import pandas as pd


class DataReaderInterface(ABC):
    """Interface for reading data from an internal (trusted) source, such as a database or output from this program"""

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


class SaverInterface(ABC):
    """Object that saves other objects to a certain place"""

    @abstractmethod
    def save(self, element: SaveableInterface):
        raise NotImplementedError


class SaveableInterface(ABC):
    """Object that is saveable in some way"""

    @abstractmethod
    def save_to(self, saver: SaverInterface):
        raise NotImplementedError


class GraphInterface(ABC):
    """Generic graph object that serves as a wrapper for other types of graphs"""

    @abstractmethod
    def render(self):
        raise NotImplementedError
