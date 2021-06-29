import importlib

import numpy as np
import pandas as pd
from astropy.time import Time
from feets import FeatureSpace
from feets.preprocess import remove_noise

import differential_photometry.rao_utilities as util


def calculate_all_feets_indices(
    data: np.ndarray, timeline: Time, uncertainties: np.ndarray
) -> list:
    """ Runs through an entire set of datasets and calculates every 
    single feature detailed in the FEETS featurelist that's relevant to time, magnitude and error

    Keyword arguments:
    data          -- a dataset of magnitudes for a sequence of stars, one star per row.
    timeline      -- the time from beginning to end of the data collection, not unique per star
    uncertainties -- error in the magnitudes
    """

    result = []  # Easier to append to a list
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        time, sample, uncertainty = remove_noise(
            timeline, sample, uncertainty, error_limit=3, std_limit=5
        )
        lc = (time, sample, uncertainty)
        feature_space = FeatureSpace(data=["time", "magnitude", "error"])
        features, values = feature_space.extract(*lc)
        result.append(dict(zip(features, values)))
    return result


def normalize(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and normalizes it to between 0-1 """
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data - data_min) / (data_max - data_min)
    return normalized


def normalize_to_median(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and brings the median to 1"""
    median = np.median(data)
    return data / median


def timeseries_largest_range(**data):
    result = []
    for d in data.values():
        d = np.abs(d)
        max_variation = (d.max(axis=1) - d.min(axis=1)).max()
        result.append(max_variation)
    return dict(zip(data.keys(), result))
