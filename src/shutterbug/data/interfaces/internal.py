from abc import ABC, abstractmethod
from functools import singledispatchmethod
from typing import Generator
from shutterbug.data.star import Star

import pandas as pd
from typing import Iterable, overload


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
