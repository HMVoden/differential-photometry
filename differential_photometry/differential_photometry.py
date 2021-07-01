import logging

import numpy as np
import pandas as pd

import differential_photometry.utilities as util


def subtract_varying_magnitudes(raw_mags: np.ndarray,
                                varying_mags: np.ndarray):
    varying_mags_subtracted = []
    for mag in varying_mags.transpose():
        delta = calculate_timeseries_differential_magnitude(
            mag, raw_mags.transpose())
        varying_mags_subtracted.append(delta)
    varying_mags_subtracted = np.array(varying_mags_subtracted)
    return varying_mags_subtracted


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
            target=target_star_error,
            reference=reference_star_errors.transpose())

        all_uncertainties.append(uncertainty)
    return np.array(all_uncertainties)


def calculate_varying_error(raw_errors: np.ndarray,
                            varying_errors: np.ndarray) -> np.ndarray:
    varying_uncertainties = []

    for err in varying_errors.transpose():
        uncertainty = calculate_timeseries_differential_uncertainty(
            target=err, reference=raw_errors.transpose())
        varying_uncertainties.append(uncertainty)
    varying_uncertainties = np.array(varying_uncertainties)
    return varying_uncertainties


def calculate_timeseries_differential_magnitude(
        target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_timeseries_differential_uncertainty(
        target: np.ndarray, reference: np.ndarray) -> np.ndarray:
    """Calculates a single timeseries differential magnitude uncertainty """
    return np.sqrt(target**2 + reference**2)


def calculate_differential_photometry(df: pd.DataFrame) -> pd.DataFrame:

    frames = []
    required_cols = ["mag", "error"]
    non_varying = df[df["varying"] == False]
    varying = df[df["varying"] == True]

    if (not varying.empty):
        # ensure that no varying stars are in reference dataset
        non_varying = df[df["varying"] == False]
        ref_raw = util.arrange_time_star(non_varying, required_cols)
        var_raw = util.arrange_time_star(varying, required_cols)

        subtracted_varying_mags = subtract_varying_magnitudes(
            raw_mags=ref_raw["mag"], varying_mags=var_raw["mag"])

        subtracted_varying_err = calculate_varying_error(
            raw_errors=ref_raw["error"], varying_errors=var_raw["error"])

        N_var = subtracted_varying_mags[0].shape[0]

        average_varying_mags = np.mean(subtracted_varying_mags, axis=1)
        average_varying_err = (
            np.sqrt(np.sum(subtracted_varying_err**2, axis=1)) / N_var)

        average_varying = util.arrange_for_dataframe(varying,
                                                     average_varying_mags,
                                                     average_varying_err)
        average_varying = {
            "average_diff_mags": average_varying[0],
            "average_uncertainties": average_varying[1],
        }
        varying = varying.assign(**average_varying)
        frames.append(varying)
    else:
        ref_raw = util.arrange_time_star(non_varying, required_cols)

    subtracted_mags = subtract_all_magnitudes(ref_raw["mag"])
    subtracted_err = calculate_all_uncertainties(ref_raw["error"])

    N = subtracted_mags[0].shape[0]

    average_diff_mags = np.mean(subtracted_mags, axis=1)
    average_error = np.sqrt(np.sum(subtracted_err**2, axis=1)) / N

    average = util.arrange_for_dataframe(non_varying, average_diff_mags,
                                         average_error)
    average = {
        "average_diff_mags": average[0],
        "average_uncertainties": average[1]
    }

    non_varying = non_varying.assign(**average)
    frames.append(non_varying)

    return pd.concat(frames, join="outer")
