import pandas as pd
from typing import List

import shutterbug.stats.utilities as stat_utils
import shutterbug.timeseries.timeseries as ts


def test_stationarity(
    data: List[float], method: str = "adf_gls", clip: bool = False
) -> pd.DataFrame:
    """Takes a dataframe containing a numerical data column and applies the specified
    statistical test on it, then compares the resulting p-value to the threshold value.
    Some tests, such as the Dickson-Fuller test, have a null hypothesis that the timeseries in question
    is non-stationary and if we want to know if a star is variable we must set the null to 'accept' that hypothesis.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing numerical timeseries columns and a name column to group by
    method : str, optional
        Statistical test name, by default "chisquared"
    threshold : float, optional
        The p-value threshold on which we want to reject or accept the hypothesis, by default 0.05
    null : str, optional
        Whether we want to accept or reject the hypothesis to know if a star is variable, by default "accept"
    clip : bool, optional
        Whether to sigma clip the data and possibly error for the statistical test, by default False
    data_name : str, optional
        The data column to operate the varying star detection on, by default "mag"

    Returns
    -------
    pd.DataFrame
        Dataframe containing the statistical test column and a "varying" truth column
    """
    if method == "chisquared":
        stat_function = stat_utils.reduced_chi_square
    if method == "adfuller":
        stat_function = stat_utils.augmented_dfuller
    if method == "kpss":
        stat_function = stat_utils.kpss
    if method == "zivot_andrews":
        stat_function = stat_utils.zastat
    if method == "adf_gls":  # best one so far
        stat_function = stat_utils.adf_gls
    test_statistic = stat_runner(data=data, stat_func=stat_function, clip=clip)

    return test_statistic


def stat_runner(
    data: List[float],
    stat_func,
    error: List[float] = None,
    clip: bool = False,
):
    """Helper function that allows for a pandas Dataframe to
    use its Apply method on a stats function and get a result column out of it

    Parameters
    ----------
    df : pd.DataFrame
        Passed in dataframe from Apply, contains the data_name and error_name as column labels if applicable.
    data_name : str
        Name of the numerical column to be worked on.
    stat_func : Callable[[np.ndarray] np.ndarray]
        The statistical function to be called on the data_name.
    error_name : str, optional
        Name of the numerical column containing the error (sigma) of the data. Requires the stat_func to have two inputs. By default None.
    clip : bool, optional
        Whether or not to sigma clip the data and mask the error, if applicable, by default False.

    Returns
    -------
    float
        A test statistic p-value from the assigned stat function
    """
    if clip == True:
        return ts.sigma_clip_data(data, stat_func, error)
    if error is not None:
        return stat_func(data, error)
    else:
        return stat_func(data)
