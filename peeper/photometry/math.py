from typing import Callable, List, Tuple

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
    subtracted_mags = np.asanyarray(subtracted_mags)
    calculated_errors = np.asanyarray(calculated_errors)

    N = subtracted_mags[0].shape[0]

    average_diff_mags = np.mean(subtracted_mags, axis=1)
    average_error = np.sqrt(np.sum(calculated_errors ** 2, axis=1)) / N

    return average_diff_mags, average_error


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
