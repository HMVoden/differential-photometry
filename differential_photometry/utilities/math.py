from typing import Callable, Dict, List

import numpy as np
import pandas as pd
from astropy.time import Time
from astropy.stats import sigma_clip
from feets import FeatureSpace
from feets.preprocess import remove_noise


def calculate_all_feets_indices(data: np.ndarray, timeline: Time,
                                uncertainties: np.ndarray) -> list:
    """Runs through an entire set of datasets and calculates every 
    single feature detailed in the FEETS featurelist that's relevant to time, magnitude and error

    Parameters
    ----------
    data : np.ndarray
        Numerical data to for features to be extracted from
    timeline : Time
        Timeline of the timeseries in question
    uncertainties : np.ndarray
        Error in the data (sigma)

    Returns
    -------
    list
        Every feature extractable from the FEETs library that handles time, magnitude and error
    """

    result = []  # Easier to append to a list
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        time, sample, uncertainty = remove_noise(timeline,
                                                 sample,
                                                 uncertainty,
                                                 error_limit=3,
                                                 std_limit=5)
        lc = (time, sample, uncertainty)
        feature_space = FeatureSpace(data=["time", "magnitude", "error"])
        features, values = feature_space.extract(*lc)
        result.append(dict(zip(features, values)))
    return result


def get_largest_range(**data: Dict):
    """Finds the largest range in one part of a timeseries dataset, for example
    if you have three days of timeseries, this will find the largest range that
    can be found in a single day

    Returns
    -------
    Dict
        Dictionary of the data name passed in and the entire dataset of values as the
        dictionary value.

    Returns
    -------
    Dict
        Dictionary of the data name and the largest range for the entire dataset
    """
    result = []
    for d in data.values():
        d = np.abs(sigma_clip(d, sigma=2, axis=1, masked=False))
        max_variation = np.nanmax(
            np.abs((np.nanmax(d, axis=1) - np.nanmin(d, axis=1))))
        result.append(max_variation)
    return dict(zip(data.keys(), result))


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
