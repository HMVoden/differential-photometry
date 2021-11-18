from typing import Sequence

import numpy as np
from shutterbug.analyzer.core.interface.differential import \
    DifferentialCalculatorInterface


class DifferentialPhotometryCalculator(DifferentialCalculatorInterface):
    def differential(
        self, target: Sequence[float], reference: Sequence[Sequence[float]], axis: int
    ) -> Sequence[float]:
        # safety checks
        target_array = np.asarray(target)
        reference_array = np.asarray(reference)
        difference = reference_array - target_array
        return np.mean((difference), axis=axis)

    def differential_error(
        self, target: Sequence[float], reference: Sequence[Sequence[float]], axis: int
    ) -> Sequence[float]:
        N = len(target) + 1
        # safety checks
        target_array = np.asarray(target)
        reference_array = np.asarray(reference)
        sum_square = np.sum((target_array ** 2 + reference_array ** 2), axis=axis)
        average = np.sqrt(sum_square) / N
        return average
