from __future__ import annotations

from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generator, List

from shutterbug.data.star import Star


class Reader(ABC):
    """Interface for reading stars from a source with criteria"""

    @abstractmethod
    def similar_to(self, star: Star) -> List[Star]:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError

    @property
    @abstractmethod
    def names(self) -> List[str]:
        raise NotImplementedError


class Writer(ABC):
    """Interface for data storage module, takes in a star or a group of stars and
    writes it to a storage medium for future reference"""

    @singledispatchmethod
    @abstractmethod
    def write(self, data: Star, overwrite: bool):
        raise NotImplementedError

    @write.register
    @abstractmethod
    def _(self, data: list, overwrite: bool):
        # have to use list as type due to bug with singledispatch
        raise NotImplementedError


class Graph(ABC):
    """Generic graph object that serves as a wrapper for other types of graphs"""

    @abstractmethod
    def render(self):
        raise NotImplementedError
