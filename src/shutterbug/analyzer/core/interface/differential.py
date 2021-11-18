from abc import ABC, abstractmethod
from typing import Sequence


class DifferentialCalculatorInterface(ABC):
    @abstractmethod
    def differential(
        self, target: Sequence[float], reference: Sequence[Sequence[float]], axis: int
    ) -> Sequence[float]:
        """Calculates the average differential magnitude of a given target via the formula sqrt(sum(reference - target)), where reference and target are broadcastable to one another"""
        raise NotImplementedError

    def differential_error(
        self, target: Sequence[float], reference: Sequence[Sequence[float]], axis: int
    ) -> Sequence[float]:
        """Calculates the average differential uncertainty of a given target via the formula sqrt(sum(reference**2 + target**2)), where reference and target are broadcastable to one another"""
        raise NotImplementedError
