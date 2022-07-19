from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Iterable, List, Protocol, Union

from shutterbug.data.star import Star


class Loader(Protocol):
    """Generic interface for an object that loads star data from a source into
    memory"""

    def __iter__(self) -> Generator[Star, None, None]:
        ...

    def __len__(self) -> int:
        ...

    @property
    def names(self) -> List[str]:
        ...

    def get(self,  name: str) -> Union[Star, None]:
        ...


class Input(ABC):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Generator[Loader, None, None]:
        raise NotImplementedError


class FileLoaderFactory(Protocol):
    READABLE_TYPES: Iterable[str]

    def make_loader(self, file_path: Path) -> Loader:
        ...
