from typing import Dict

import numpy as np


def calculate_differential_magnitude(target: np.ndarray,
                                     reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_differential_uncertainty(target: np.ndarray,
                                       reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude uncertainty """
    return np.sqrt(target**2 + reference**2)


def calculate_differential_average(subtracted_mags: np.ndarray,
                                   calculated_errors: np.ndarray) -> Dict:
    N = subtracted_mags[0].shape[0]

    average_diff_mags = np.mean(subtracted_mags, axis=1)
    average_error = np.sqrt(np.sum(calculated_errors**2, axis=1)) / N

    results = {
        "average_diff_mags": average_diff_mags,
        "average_uncertainties": average_error
    }

    return results
