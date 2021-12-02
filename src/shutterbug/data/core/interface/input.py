from abc import ABC, abstractmethod
from typing import Generator, List

from shutterbug.data.core.star import Star


class InputInterface(ABC):
    @abstractmethod
    def load(self) -> Generator[Star, None, None]:
        pass
