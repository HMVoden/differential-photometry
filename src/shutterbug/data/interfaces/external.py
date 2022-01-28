from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Protocol, Set

from shutterbug.data.star import Star

from abc import ABC, abstractmethod
from typing import Generator


class InputInterface(ABC):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError
