import numpy as np
import pandas as pd
import importlib
from astropy.time import Time
from feets import FeatureSpace
from feets.preprocess import remove_noise

import rao_utilities as util


def calculate_all_feets_indices(data: np.ndarray, timeline: Time, uncertainties: np.ndarray) -> list:
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
            timeline, sample, uncertainty, error_limit=3, std_limit=5)
        lc = (time, sample, uncertainty)
        feature_space = FeatureSpace(data=['time', 'magnitude', 'error'])
        features, values = feature_space.extract(*lc)
        result.append(dict(zip(features, values)))
    return result


def subtract_varying_magnitudes(raw_mags: np.ndarray, varying_mags: np.ndarray):
    varying_mags_subtracted = []
    for mag in varying_mags.transpose():
        delta = calculate_timeseries_differential_magnitude(
            mag, raw_mags.transpose())
        varying_mags_subtracted.append(delta)
    varying_mags_subtracted = np.array(varying_mags_subtracted)
    mags_subtracted = subtract_all_magnitudes(raw_mags)
    return mags_subtracted, varying_mags_subtracted


def subtract_all_magnitudes(magnitudes: np.ndarray) -> np.ndarray:
    """For each star inputted into this function, this will take that star column, remove it from the dataset
    then subtract it from the other stars, creating an entire list of numpy arrays with a series of 'target stars'
    for use in differential photometry

    Keyword arguments:
    magnitudes -- a numpy array of star magnitudes, ordered by row=time, column=star
    """

    all_magnitudes_subtracted = []
    # Index so we can remove active column
    for index, target_star in enumerate(magnitudes.transpose()):
        # Remove 'active' column, subtract active from every other column
        reference_stars = np.delete(magnitudes, index, axis=1)
        delta = calculate_timeseries_differential_magnitude(
            target_star, reference_stars.transpose())
        all_magnitudes_subtracted.append(delta)
    return np.array(all_magnitudes_subtracted)


def calculate_all_uncertainties(errors: np.ndarray) -> np.ndarray:
    """For each star's error inputted into this function, this will take that error column, remove it from the dataset
    then square roots the sum the squares of the other columns and the removed one, 
    creating an entire list of numpy arrays with a series of 'target star errors' for use in differential photometry

    Keyword arguments:
    errors -- a numpy array of star error, ordered by row=time, column=error
    """
    all_uncertainties = []  # List so appending is not memory-intensive
    # Index so we can remove active column
    for index, target_star_error in enumerate(errors.transpose()):
        # Remove 'active' column, get uncertainty for each column
        reference_star_errors = np.delete(errors, index, axis=1)
        uncertainty = calculate_timeseries_differential_uncertainty(
            target=target_star_error, reference=reference_star_errors.transpose())

        all_uncertainties.append(uncertainty)
    return np.array(all_uncertainties)


def calculate_varying_error(raw_errors: np.ndarray, varying_errors: np.ndarray) -> np.ndarray:
    varying_uncertainties = []

    for err in varying_errors.transpose():
        uncertainty = calculate_timeseries_differential_uncertainty(
            target=err, reference=raw_errors.transpose())
        varying_uncertainties.append(uncertainty)
    varying_uncertainties = np.array(varying_uncertainties)
    uncertainties = calculate_all_uncertainties(raw_errors)
    return uncertainties, varying_uncertainties


def calculate_timeseries_differential_magnitude(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_timeseries_differential_uncertainty(target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude uncertainty """
    return np.sqrt(target**2 + reference**2)


def calculate_differential_photometry(magnitudes: np.ndarray, error: np.ndarray, num_stars: int, num_samples: int) -> np.ndarray:
    """Performs differential photometry on all stars in provided dataset

    Args:
        magnitudes (np.ndarray): Raw magnitudes from photometry
        error (np.ndarray): Error in photometry calculations
        num_stars (int): number of stars in dataset
        num_samples (int): number of samples taken of the stars

    Returns:
        np.ndarray, np.ndarray: Averaged differential magnitudes and their uncertainty
    """

    # Stack both mags and error according to time, new column = new file in time
    mags = magnitudes.values.reshape(num_samples, num_stars)
    error = error.values.reshape(num_samples, num_stars)

    # array of arrays, each array corresponding to a single star as the 'target'
    # Each individual array is organized by incrementing time in columns, rows are stars
    subtracted_magnitudes = subtract_all_magnitudes(mags)
    uncertainties = calculate_all_uncertainties(error)

    N = uncertainties[0].shape[0]
    # mean of every column, accumulating all stars at particular time
    average_diff_mags = np.mean(subtracted_magnitudes, axis=1)
    average_uncertainties = np.sqrt(np.sum(uncertainties**2, axis=1)) / N

    average_diff_mags = average_diff_mags.transpose().reshape(num_samples*num_stars, 1)
    average_uncertainties = average_uncertainties.transpose().reshape(num_samples *
                                                                      num_stars, 1)
    return average_diff_mags, average_uncertainties


def calculate_varying(df: pd.DataFrame, varying: pd.DataFrame) -> pd.DataFrame:

    varying_stars = varying['name'].unique()
    # ensure that no varying stars are in reference dataset
    reference = df[~df['name'].isin(varying_stars)]

    num_stars, num_samples = util.extract_samples_stars(reference)
    num_var, num_var_sample = util.extract_samples_stars(varying)

    raw_mags = reference['mag'].values.reshape(num_samples, num_stars)
    raw_error = reference['error'].values.reshape(num_samples, num_stars)

    varying_mags = varying['mag'].values.reshape(num_var_sample, num_var)
    varying_error = varying['error'].values.reshape(num_var_sample, num_var)

    subtracted_mags, subtracted_varying_mags = subtract_varying_magnitudes(
        raw_mags=raw_mags, varying_mags=varying_mags)

    subtracted_err, subtracted_varying_err = calculate_varying_error(
        raw_errors=raw_error, varying_errors=varying_error)

    N = num_stars - 1

    average_varying_mags = np.mean(subtracted_varying_mags, axis=1)
    average_varying_err = np.sqrt(
        np.sum(subtracted_varying_err**2, axis=1)) / (N + 1)

    average_varying_mags = average_varying_mags.transpose().reshape(num_var_sample *
                                                                    num_var, 1)
    average_varying_err = average_varying_err.transpose().reshape(num_var_sample *
                                                                  num_var, 1)

    average_diff_mags = np.mean(subtracted_mags, axis=1)
    average_error = np.sqrt(np.sum(subtracted_err**2, axis=1)) / N

    average_diff_mags = average_diff_mags.transpose().reshape(num_samples*num_stars, 1)
    average_error = average_error.transpose().reshape(num_samples *
                                                      num_stars, 1)

    varying = varying.assign(average_diff_mags=average_varying_mags)
    varying = varying.assign(average_uncertainties=average_varying_err)
    reference = reference.assign(average_diff_mags=average_diff_mags)
    reference = reference.assign(average_uncertainties=average_error)
    frames = [varying, reference]

    df = pd.concat(frames,
                   join="outer")

    return df


def normalize(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and normalizes it to between 0-1 """
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data-data_min)/(data_max - data_min)
    return normalized


def normalize_to_median(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and brings the median to 1"""
    median = np.median(data)
    return data/median
