from typing import Dict, Callable, List

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


def calculate_on_dataset(targets: List[float],
                         func: Callable[[List[float], List[float]],
                                        List[float]],
                         excluded_targets: List[float] = None) -> List[List]:
    """For each star inputted into this function, this will take that star column, remove it from the dataset
    then subtract it from the other stars, creating an entire list of numpy arrays with a series of 'target stars'
    for use in differential photometry

    Keyword arguments:
    magnitudes -- a numpy array of star magnitudes, ordered by row=time, column=star
    """
    results = []
    targets_results = []
    excluded_results = []
    targets = np.asanyarray(targets).transpose()  # safety check

    if excluded_targets is not None:
        excluded_targets = np.asanyarray(
            excluded_targets).transpose()  # safety check
        for target in excluded_targets:
            delta = func(target, targets)
            excluded_results.append(delta)

    # Index so we can remove active column
    for index, target in enumerate(targets):
        # Remove 'active' row, subtract active from every other row
        reference = np.delete(targets, index, axis=0)
        delta = func(target, reference)
        targets_results.append(delta)

    results.append(np.array(targets_results))
    if not (len(excluded_results) == 0):
        results.append(np.array(excluded_results))
    return results