from abc import ABC, abstractmethod

from shutterbug.data.core.star import Star


class WriterInterface(ABC):
    """Interface for data storage module, takes in a star or a group of stars and writes it to a storage medium for future reference"""

    @abstractmethod
    def write(self, data: Star) -> bool:
        raise NotImplementedError
