from abc import ABC, abstractmethod
from typing import Generator
from shutterbug.data.interfaces.internal import LoaderInterface
from shutterbug.data.star import Star

from abc import ABC, abstractmethod
from typing import Generator, Iterable, Protocol
from pathlib import Path


class InputInterface(ABC):
    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Generator[Star, None, None]:
        raise NotImplementedError


class FileLoaderFactory(Protocol):
    READABLE_TYPES: Iterable[str]

    def make_loader(self, file_path: Path) -> LoaderInterface:
        ...
