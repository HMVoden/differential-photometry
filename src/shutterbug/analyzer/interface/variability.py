from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional, Sequence


class VariabilityDetectionInterface(ABC):
    @abstractmethod
    def detect(
        self,
        data: Sequence[float],
        uncertainty: Optional[Sequence[float]],
    ) -> float:
        raise NotImplementedError
