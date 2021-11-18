from abc import ABC, abstractmethod
from typing import Dict, Sequence


class VariableStarDetectionInterface(ABC):
    @abstractmethod
    def detect_variability(self, lightcurve: Sequence[float]) -> Dict:
        raise NotImplementedError
