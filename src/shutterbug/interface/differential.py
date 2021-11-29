from abc import ABC, abstractmethod
from typing import Literal, Sequence


class DifferentialCalculatorInterface(ABC):
    @abstractmethod
    def calculate(
        self,
        method: Literal["difference", "error"],
        target: Sequence[float],
        reference: Sequence[Sequence[float]],
        axis: int,
    ) -> Sequence[float]:
        """Calculates either the average difference or the average difference error of the target and reference sequences along given axis."""
        raise NotImplementedError
