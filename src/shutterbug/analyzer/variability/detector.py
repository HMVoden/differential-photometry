from dataclasses import dataclass
from typing import Dict, Literal, Optional, Sequence, Tuple

from shutterbug.analyzer.core.interface.variability import \
    VariabilityDetectionInterface
from shutterbug.analyzer.variability.result import TestResult
from shutterbug.analyzer.variability.test_interface import (
    VariabilityDataTestInterface, VariabilityTestInterface,
    VariabilityUncertaintyTestInterface)


@dataclass
class VariabilityDetector(VariabilityDetectionInterface):
    variability_tester: VariabilityTestInterface
    pvalue: float

    def detect(
        self,
        data: Sequence[float],
        uncertainty: Optional[Sequence[float]] = None,
    ) -> Tuple[float, bool]:
        if type(self.variability_tester) == VariabilityUncertaintyTestInterface:
            result = self.variability_tester.test(data=data, uncertainty=uncertainty)
        elif type(self.variability_tester) == VariabilityDataTestInterface:
            result = self.variability_tester.test(data=data)
        else:
            raise ValueError(
                f"Statistical test is of unknown type {type(self.variability_tester)}"
            )
        return (self._is_variable(result), result.pvalue)

    def _is_variable(self, result: TestResult):
        result_pvalue = result.pvalue
        test_pvalue = self.pvalue
        null = result.null
        if null == "accept":
            return result_pvalue > test_pvalue
        elif null == "reject":
            return result_pvalue <= test_pvalue
