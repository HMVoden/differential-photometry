from abc import ABC, abstractmethod
from typing import Generator
from shutterbug.data.interfaces.internal import GraphInterface, LoaderInterface
from shutterbug.data.star import Star

from abc import ABC, abstractmethod
from typing import Generator, Iterable, Protocol, Optional, Tuple
from pathlib import Path
import pandas as pd


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


class GraphBuilderInterface(Protocol):
    """Generic Graph builder wrapper, for any graph system"""

    @property
    def title(self) -> Optional[str]:
        ...

    @property
    def axis_names(self) -> Tuple[Optional[str], Optional[str]]:
        ...

    @property
    def axis_limits(self) -> Tuple[Optional[float], Optional[float]]:
        ...

    @property
    def size(self) -> Tuple[Optional[float], Optional[float]]:
        ...

    @property
    def data(self) -> pd.Series:
        ...

    @property
    def type(self) -> str:
        ...

    def reset(self) -> None:
        ...

    def build(self) -> GraphInterface:
        ...
