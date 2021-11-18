from abc import ABC, abstractmethod
from typing import Iterable, Sequence


class ConstraintInterface(ABC):
    @abstractmethod
    def meets(self, values: Sequence) -> Iterable[int]:
        """Goes through values given and returns indices of all values that meet criteria"""
        raise NotImplementedError
