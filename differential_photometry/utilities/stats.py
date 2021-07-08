from logging import error
import numpy as np
import pandas as pd

from typing import List
from astropy.stats import sigma_clip


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
        return sigma_clip_data(data, stat_func, error)
    if error is not None:
        return stat_func(data, error)
    else:
        return stat_func(data)


def sigma_clip_data(data: List[float],
                    stat_func,
                    error: List[float] = None) -> pd.DataFrame:
    """A secondary runner for a pandas Apply, sigma clips the data in the data_name column from the dataframe
    before running the stat function on the data column.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the numerical columns data_name and error_name if applicable.
    data_name : str
        Column label of the numerical data in the dataframe.
    stat_func : Callable[[np.ndarray, np.ndarray=None] float]
        statistical function returning the p-value from the statistical function in question.
    error_name : str, optional
        Column label of the numerical error of the data in the dataframe, by default None.

    Returns
    -------
    pd.DataFrame
        Dataframe containing the p-values calculated by the statistical function.
    """
    sample = sigma_clip(data, sigma=3, masked=True)
    if error is not None:
        error = np.ma.array(error, mask=sample.mask)
        return stat_func(sample, error)
    return stat_func(sample)
