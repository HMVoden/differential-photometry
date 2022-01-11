from abc import ABC, abstractmethod
from typing import Generator

import pandas as pd


class DataReaderInterface(ABC):
    @property
    @abstractmethod
    def all(self) -> Generator[pd.DataFrame, None, None]:
        raise NotImplementedError

    @abstractmethod
    def similar_to(self, star: str) -> pd.DataFrame:
        raise NotImplementedError
