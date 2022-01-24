from typing import Literal, Optional, Sequence

import numpy as np
import numpy.typing as npt


class DifferentialPhotometryCalculator:
    def calculate(
        self,
        method: Literal["difference", "error"],
        target: Sequence[float],
        reference: Sequence[Sequence[float]],
        axis: Optional[int] = None,
    ) -> Sequence[float]:
        # safety checks
        target_array = np.asarray(target)
        reference_array = np.asarray(reference)
        if method == "difference":
            return self._average_difference(
                target=target_array, reference=reference_array, axis=axis
            )
        elif method == "error":
            return self._average_error(
                target=target_array, reference=reference_array, axis=axis
            )
        else:
            raise ValueError(
                f"Passed in unknown method {method}, expected 'difference' or 'error'"
            )

    def _average_error(
        self,
        target: npt.NDArray[np.float64],
        reference: npt.NDArray[np.float64],
        axis: Optional[int] = None,
    ) -> Sequence[float]:
        N = len(target) + 1
        sum_square = np.sum((target ** 2 + reference ** 2), axis=axis)
        average = np.sqrt(sum_square) / N
        return average

    def _average_difference(
        self,
        target: npt.NDArray[np.float64],
        reference: npt.NDArray[np.float64],
        axis: Optional[int] = None,
    ):
        difference = reference - target
        return np.mean((difference), axis=axis)
