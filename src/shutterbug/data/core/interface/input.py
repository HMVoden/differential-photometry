from abc import ABC, abstractmethod
from typing import Generator, List

from shutterbug.data.core.star import Star


class InputInterface(ABC):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError
    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError
