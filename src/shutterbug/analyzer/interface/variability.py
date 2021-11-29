from abc import ABC, abstractmethod
from typing import Optional, Sequence, Tuple


class VariabilityDetectionInterface(ABC):
    @abstractmethod
    def detect(
        self,
        data: Sequence[float],
        uncertainty: Optional[Sequence[float]],
    ) -> Tuple[float, bool]:
        raise NotImplementedError
