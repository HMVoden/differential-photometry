import logging
from math import isclose

import numpy as np
import pandas as pd
from astropy.modeling import fitting, models
from astropy.stats import sigma_clip
from wotan import flatten

import rao_data as data
import rao_stats as stat
import rao_utilities as util


def find_varying_stars(df: pd.DataFrame) -> pd.DataFrame:
    """Uses a reduced chi-squared test on a dataframe's data to find varying stars in that data

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe that has been appropriately cleaned and setup

    Returns
    -------
    pd.DataFrame
        Two dataframes, first contains all the varying stars and second contains all the non-varying stars
    """

    df['varying'] = False  # Add metadata to dataframe
    df['chisquared'] = 0.0

    stars = df['name'].unique()
    time = df['jd'].unique()
    window = time.mean()/4
    columns = ['mag', 'error']

    arranged_cols = util.arrange_time_star(df, columns)

    mags = arranged_cols['mag'].transpose()
    errors = arranged_cols['error'].transpose()

    all_chi = []
    for i, sample in enumerate(mags):
        sample = sigma_clip(sample, sigma_upper=6, sigma_lower=20)
        error = errors[i]
        chi = stat.reduced_chi_square(sample, error)
        if chi > 10.0:
            df.loc[df['name'] == stars[i], 'varying'] = True
            df.loc[df['name'] == stars[i], 'chisquared'] = chi
        else:
            df.loc[df['name'] == stars[i], 'chisquared'] = chi
        all_chi.append(chi)

    varying = df[df['varying'] == True]  # Split by varying and non-varying.
    non_varying = df[df['varying'] == False]
    logging.debug("Chi squared of all stars %r: ", dict(zip(stars, all_chi)))
    logging.info("Number of stars processed: %s", len(stars))
    logging.info("Number of stars found to be varying: %s",
                 varying['name'].nunique())

    return non_varying, varying


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
    num_stars, num_samples = data.extract_samples_stars(df)

    degree = polynomial_degree

    logging.debug(
        "finding trend in dataframe with %s stars and %s samples", num_stars, num_samples)

    # get data and organize it properly by time = row, column = star
    non_varying_mags = df['mag'].to_numpy(dtype='float64').reshape(
        num_samples, num_stars)
    non_varying_error = df['error'].to_numpy(dtype='float64').reshape(
        num_samples, num_stars)

    average_mag = np.average(non_varying_mags, axis=1)
    average_error = np.sum(non_varying_error**2, axis=1)/num_stars

    timeline = df['jd'].unique()  # Our x-axis
    weight = 1/average_error**2   # Uncertainty weighting

    fit = fitting.LinearLSQFitter()  # Assuming linear dataset
    # Chebyshev seems to work better than polynomial
    poly = models.Chebyshev1D(degree=degree)
    fitted_poly = fit(model=poly, x=timeline, y=average_mag, weights=weight)

    # Get calculated parameters from model
    general_parameters = dict(
        zip(fitted_poly.param_names, fitted_poly.parameters))
    logging.debug("Parameters in found trend: %r", general_parameters)
    # Set y-intercept to 0 so that trend hovers around 0
    general_parameters['c0'] = 0

    dataset_trend = models.Chebyshev1D(
        degree=degree, domain=fitted_poly.domain, **general_parameters)

    return dataset_trend(timeline)  # return trend around 0


def detrend_dataset(df: pd.DataFrame, trend: np.ndarray) -> pd.DataFrame:
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
    data_with_trend = util.arrange_time_star(df, ['mag'])['mag']
    data_detrended = data_with_trend.transpose() - trend
    # reshape to re-insert into dataframe
    data_detrended = util.arrange_for_dataframe(df, data_detrended)[0]
    return df.assign(mag=data_detrended)


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
        trend, expected=0, parameters_estimated=parameters_fit)
    is_constant = isclose(chisquared, 1, abs_tol=0.2)  # expected very close
    return is_constant


def find_biweight_trend(df: pd.DataFrame):
    required_cols = ['mag', 'error']
    non_varying = util.arrange_time_star(df, required_cols)
    mag = non_varying['mag']
    error = non_varying['error']
    N = mag[0].shape[0]

    timeline = df['jd'].unique()
    time = (timeline - timeline.min())
    window = time.max()/4

    average = np.average(mag, axis=1)
    av_error = np.sum(error**2, axis=1)/N

    w_avg = stat.weighted_mean(average, av_error)

    _, trend = flatten(
        time,

        average,
        method='biweight',
        window_length=window,
        edge_cutoff=window/2,
        return_trend=True,
        cval=5.0
    )
    logging.info('Biweight trend was found to be %r', trend)

    return (trend-w_avg)
