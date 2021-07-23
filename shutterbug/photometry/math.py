from typing import Callable, List, Tuple
from numba import guvectorize, float64, float32
from math import sqrt
from numba.core.types.scalars import Float

import numpy as np


def calculate_differential_magnitude(
    target: np.ndarray, reference: np.ndarray
) -> np.ndarray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_differential_uncertainty(
    target: np.ndarray, reference: np.ndarray
) -> np.ndarray:
    """Calculates a single timeseries differential magnitude uncertainty"""
    return np.sqrt(target ** 2 + reference ** 2)


def calculate_differential_average(
    subtracted_mags: np.ndarray, calculated_errors: np.ndarray
) -> Tuple[List[float], List[float]]:
    avg_diff_mags = average_differential_magnitudes(subtracted_mags)
    avg_error = average_error(calculated_errors)

    return avg_diff_mags, avg_error


# guvectorize intentionally does not return.
@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average_differential_magnitudes(
    subtracted_magnitudes: List[float], res: List
) -> float:
    N = len(subtracted_magnitudes)
    res = 0
    for mag in subtracted_magnitudes:
        res = res + mag
    res = res / N


@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average_error(errors: List[float], res: List) -> float:
    N = len(errors)
    res = 0
    for error in errors:
        res = res + error ** 2
    res = sqrt(res) / N


def calculate_on_dataset(
    targets: List[float],
    func: Callable[[List[float], List[float]], List[float]],
    excluded: List[float],
) -> List[List]:
    """For each star inputted into this function, this will take that star column, remove it from the dataset
    then subtract it from the other stars, creating an entire list of numpy arrays with a series of 'target stars'
    for use in differential photometry

    Keyword arguments:
    magnitudes -- a numpy array of star magnitudes, ordered by row=time, column=star
    """
    results = []
    excluded_results = []
    targets = np.asanyarray(targets).transpose()  # Safety check
    excluded_targets = np.asanyarray(excluded).transpose()

    for target in excluded_targets:
        delta = func(target, targets)
        excluded_results.append(delta)

    for index, target in enumerate(targets):
        delta = func(target, np.delete(targets, index, axis=0))
        results.append(delta)

    return results, excluded_results
