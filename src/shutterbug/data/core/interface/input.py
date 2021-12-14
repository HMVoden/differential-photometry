from abc import ABC, abstractmethod
from typing import Generator

from shutterbug.data.core.interface.loader import LoaderInterface


class InputInterface(ABC):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Generator[LoaderInterface, None, None]:
        raise NotImplementedError
