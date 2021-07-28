import numpy as np
import pandas as pd
from typing import List
from arch.unitroot import ADF, DFGLS, KPSS, ZivotAndrews
from scipy.stats import chisquare

import config.manager as config


from typing import Any


def reduced_chi_square(
    data: List[float], expected: List[float] = None, parameters_estimated: int = None
):
    """Computes the reduced chi squared of a given dataset and returns
    a value that should be approximately 1. If the value is greatly less than one
    the expected dataset has errors that are overestimated for the dataset.

    If the value is greatly more than one the expected values are a bad fit for the
    data.

    Parameters
    ----------
    data : list-like
        Data to have the reduced chi squared performed on
    error : list-like, optional
        Error(sigma) of the data, by default None
    expected : list-like, optional
        The expected data, must be same size as data, by default None
    parameters_estimated : int, optional
        The parameters estimated already in calculates, by default None

    Returns
    -------
    float
        The reduced chi squared test statistic
    """
    # This is ugly and can be handled better
    data = np.asanyarray(data)
    if parameters_estimated is None:
        parameters_estimated = 1
    if expected is None:
        parameters_estimated += 1
        expected = np.median(data)
    variance = np.var(data, ddof=1)
    dof = data.shape[0] - parameters_estimated - 1
    chi = np.sum(((data - expected) ** 2 / variance)) / dof
    # print(chi)
    return chi


def regular_chi_square(data, error=None):
    """Performs the chi squared test on the provided data.

    Further reading: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html#scipy.stats.chisquare

    Configured in stats.toml

    Parameters
    ----------
    data : list-like
        Data to be tested
    error : list-like, optional
        Error(sigma) of data, must be same size as data, by default None

    Returns
    -------
    float
        p-value of the chi squared test
    """
    stats_config = config.get("stats")
    expected_switch = stats_config["chisquared"]["expected"]
    ddof = stats_config["chisquared"]["ddof"]
    expected = None
    if expected_switch == "mean":
        expected = np.average(data)
    elif expected_switch == "median":
        expected = np.median(data)
    elif expected_switch == "weighted_mean":
        expected = np.average(data, weights=(1 / error ** 2))

    result = chisquare(f_obs=data, f_exp=expected, ddof=ddof)
    print(result)
    return result[1]  # p-value


def augmented_dfuller(data: List[float]) -> float:
    """Performs the augmented Dickey-Fuller test on the data.
    The null hypothesis of this test is that the timeseries inputted is NOT stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.ADF.html

    This is configured in stats.toml

    Parameters
    ----------
    data : list-like
        Timeseries to test stationarity on

    Returns
    -------
    float
        the p-value of the test statistic
    """
    stats_config = config.get("stats")
    result = ADF(data, **stats_config["adfuller"])
    # print(result)
    return result.pvalue


def kpss(data: List[float]) -> float:
    """Performs the Kwiatkowski–Phillips–Schmidt–Shin test of stationarity on the inputted data.
    The null hypothesis of this test is that the timeseries inputted is stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.DFGLS.html#arch.unitroot.DFGLS

    This is configured in stats.toml

    Parameters
    ----------
    data : list-like
        Timeseries to test stationarity on

    Returns
    -------
    float
        the p-value of the test statistic
    """
    stats_config = config.get("stats")
    result = KPSS(data, **stats_config["kpss"])
    return result.pvalue


def zastat(data: List[float]) -> float:
    """Performs the non-parametric Zivot-Andrews test of timeseries
    stationarity on the inputted data.
    The null hypothesis of this test is that the timeseries inputted is stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.ZivotAndrews.html

    This is configured in stats.toml

    Parameters
    ----------
    data : list-like
        Timeseries to test stationarity on

    Returns
    -------
    float
        the p-value of the test statistic
    """
    stats_config = config.get("stats")
    result = ZivotAndrews(data, **stats_config["zivot_andrews"])
    return result.pvalue


def adf_gls(data: List[float]) -> float:
    """Performs the GLS-version of the augmented Dickey-Fuller test on the data.
    The null hypothesis of this test is that the timeseries inputted is
    NOT stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.DFGLS.html#arch.unitroot.DFGLS

    This is configured in stats.toml

    Parameters
    ----------
    data : list-like
        Timeseries to test stationarity on

    Returns
    -------
    float
        the p-value of the test statistic
    """
    stats_config = config.get("stats")
    result = DFGLS(data, **stats_config["adf_gls"])
    return result.pvalue


def normalize(data: np.ndarray) -> np.ndarray:
    """Takes a dataset and normalizes it to between 0-1

    Parameters
    ----------
    data : np.ndarray
        Data to normalize

    Returns
    -------
    np.ndarray
        Normalized data
    """
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data - data_min) / (data_max - data_min)
    return normalized


def normalize_to_std(df: pd.DataFrame) -> pd.DataFrame:
    """Finds the mean of every numerical column in the dataframe, its standard deviation
    then converts it to a z-score. For use in machine learning

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing numerical values to normalize (in a Gaussian sense)

    Returns
    -------
    pd.DataFrame
        Dataframe that has been normalized
    """
    df_mean = df.mean()
    df_std = df.std()
    df_norm = (df - df_mean) / df_std
    return df_norm


def normalize_to_median(data: np.ndarray) -> np.ndarray:
    """Takes a dataset and brings the median to 1

    Parameters
    ----------
    data : np.ndarray
        Dataset to normalize

    Returns
    -------
    np.ndarray
        Normalized dataset
    """
    median = np.median(data)
    return data / median
