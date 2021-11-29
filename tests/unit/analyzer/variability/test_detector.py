from dataclasses import dataclass
from typing import Literal, Sequence

import pytest
from shutterbug.analyzer.variability.detector import VariabilityDetector
from shutterbug.analyzer.variability.result import TestResult
from shutterbug.analyzer.variability.test_interface import (
    VariabilityDataTestInterface, VariabilityTestInterface,
    VariabilityUncertaintyTestInterface)


@dataclass
class MockTest(VariabilityTestInterface):
    null: Literal["accept", "reject"]
    pvalue: float

    def test(self, data: Sequence[float]) -> TestResult:
        return TestResult(null=self.null, pvalue=self.pvalue)


class MockUncertaintyTest(VariabilityUncertaintyTestInterface):
    null: Literal["accept", "reject"]
    pvalue: float

    def test(self, data: Sequence[float]) -> TestResult:
        return TestResult(null=self.null, pvalue=self.pvalue)


class MockDataTest(VariabilityDataTestInterface):
    null: Literal["accept", "reject"]
    pvalue: float

    def test(self, data: Sequence[float]) -> TestResult:
        return TestResult(null=self.null, pvalue=self.pvalue)


def test_reject_is_variable():
    mock_test = MockTest(null="reject", pvalue=0.02)
    detector = VariabilityDetector(variability_tester=mock_test, pvalue=0.05)
    test_result = mock_test.test([1, 2, 3, 4])
    is_variable_bool = detector._is_variable(test_result)
    assert is_variable_bool


def test_accept_is_variable():
    mock_test = MockTest(null="accept", pvalue=0.02)
    detector = VariabilityDetector(variability_tester=mock_test, pvalue=0.05)
    test_result = mock_test.test([1, 2, 3, 4])
    is_variable_bool = detector._is_variable(test_result)
    assert not is_variable_bool
