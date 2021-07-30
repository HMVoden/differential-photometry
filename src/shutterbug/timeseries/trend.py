import logging
from math import isclose

import astropy.modeling.fitting as fitting
import astropy.modeling.models as models
import shutterbug.stats.utilities as stat
import numpy as np
import pandas as pd
import shutterbug.data.utilities as data_util

from wotan import flatten


def find_biweight_trend(df: pd.DataFrame):
    required_cols = ["mag", "error"]
    non_varying = data_util.arrange_time_star(df, required_cols)
    mag = non_varying["mag"]
    error = non_varying["error"]
    N = mag[0].shape[0]

    timeline = df["jd"].unique()
    time = timeline - timeline.min()
    window = time.max() / 10

    average = np.average(mag, axis=1)
    av_error = np.sum(error ** 2, axis=1) / N

    w_avg = stat.weighted_mean(average, av_error)

    _, trend = flatten(
        time,
        average,
        method="biweight",
        window_length=window,
        # edge_cutoff=window/4,
        return_trend=True,
        cval=5.0,
    )
    # logging.info("Biweight trend was found to be %r", trend)

    return trend - w_avg


def is_trend_constant(trend: np.ndarray, parameters_fit: int = None) -> bool:
    """Checks if the trend is approximately a straight line hovering around 0

    Parameters
    ----------
    trend : np.ndarray
        Trend of a dataset
    parameters_fit : int, optional
        Number of parameters the trend fitting used, by default None

    Returns
    -------
    bool
        Whether or not the trend is a constant around 0
    """
    if parameters_fit is None:
        parameters_fit = 0
    chisquared = stat.reduced_chi_square(
        data=trend, expected=0, parameters_estimated=parameters_fit
    )
    is_constant = isclose(chisquared, 1, abs_tol=0.2)  # expected very close
    logging.info("Chisquared for trend found to be %s", chisquared)
    return is_constant


def detrend(df: pd.DataFrame, trend: np.ndarray) -> pd.DataFrame:
    """Removes trend from dataset

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe that has been appropriately cleaned and setup
    trend : np.ndarray
        The previously determined trend in the dataset

    Returns
    -------
    pd.DataFrame
        The original dataframe with the magnitudes detrended
    """

    # get data and organize it properly by time = row, column = star
    data_with_trend = data_util.arrange_time_star(df, ["mag"])["mag"]
    data_detrended = data_with_trend.transpose() - trend
    # reshape to re-insert into dataframe
    data_detrended = data_util.arrange_for_dataframe(df, data_detrended)[0]
    return df.assign(mag=data_detrended)


def find_polynomial_trend(df: pd.DataFrame, polynomial_degree: int = 8) -> np.ndarray:
    """Calculates a Chebyshev polynomial on top of averaged data of a dataset to find a trend in the entire dataset

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe that has been appropriately cleaned and setup
    polynomial_degree : int, optional
        The polynomial degree of the Chebyshev polynomial, by default 8

    Returns
    -------
    np.ndarray
        The trend, hovering around 0, that has been found in an entire averaged dataset
    """
    num_stars, num_samples = data_util.extract_samples_stars(df)

    degree = polynomial_degree

    logging.debug(
        "finding trend in dataframe with %s stars and %s samples",
        num_stars,
        num_samples,
    )

    # get data and organize it properly by time = row, column = star
    non_varying_mags = (
        df["mag"].to_numpy(dtype="float64").reshape(num_samples, num_stars)
    )
    non_varying_error = (
        df["error"].to_numpy(dtype="float64").reshape(num_samples, num_stars)
    )

    average_mag = np.average(non_varying_mags, axis=1)
    average_error = np.sum(non_varying_error ** 2, axis=1) / num_stars

    timeline = df["jd"].unique()  # Our x-axis
    weight = 1 / average_error ** 2  # Uncertainty weighting

    fit = fitting.LinearLSQFitter()  # Assuming linear dataset
    # Chebyshev seems to work better than polynomial
    poly = models.Chebyshev1D(degree=degree)
    fitted_poly = fit(model=poly, x=timeline, y=average_mag, weights=weight)

    # Get calculated parameters from model
    general_parameters = dict(zip(fitted_poly.param_names, fitted_poly.parameters))
    logging.debug("Parameters in found trend: %r", general_parameters)
    # Set y-intercept to 0 so that trend hovers around 0
    general_parameters["c0"] = 0

    dataset_trend = models.Chebyshev1D(
        degree=degree, domain=fitted_poly.domain, **general_parameters
    )

    return dataset_trend(timeline)  # return trend around 0
