from abc import ABC, abstractmethod
from typing import Dict, Literal, Optional, Sequence

from shutterbug.analyzer.variability.result import TestResult


class VariabilityTestInterface(ABC):
    null: Literal["accept", "reject"]

    @abstractmethod
    def test(self, **kwargs) -> TestResult:
        raise NotImplementedError


class VariabilityUncertaintyTestInterface(VariabilityTestInterface):
    @abstractmethod
    def test(self, data: Sequence[float], uncertainty: Sequence[float]) -> TestResult:
        raise NotImplementedError


class VariabilityDataTestInterface(VariabilityTestInterface):
    @abstractmethod
    def test(self, data: Sequence[float]) -> TestResult:
        raise NotImplementedError
