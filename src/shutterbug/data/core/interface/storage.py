from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Iterable
from shutterbug.data.core.star import Star


class StorageInterface(ABC):
    """Interface for data storage module, takes in a star or a group of stars and writes it to a storage medium for future reference"""

    @abstractmethod
    @singledispatchmethod
    def store(self, data: Star) -> bool:
        raise NotImplementedError

    @abstractmethod
    @store.register
    def _(self, data: Iterable[Star]) -> bool:
        raise NotImplementedError
