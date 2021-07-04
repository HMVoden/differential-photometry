import numpy as np
import pandas as pd
from astropy.stats import sigma_clip


def stat_runner(
    df: pd.DataFrame,
    data_name: str,
    stat_func,
    error_name: str = None,
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
        return sigma_clip_data(df, data_name, stat_func, error_name)
    if error_name is not None:
        return stat_func(df[data_name], df[error_name])
    else:
        return stat_func(df[data_name])


def sigma_clip_data(df: pd.DataFrame,
                    data_name: str,
                    stat_func,
                    error_name: str = None) -> pd.DataFrame:
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
    sample = sigma_clip(df[data_name], sigma=3, masked=True)
    if error_name is not None:
        error = np.ma.array(df[error_name], mask=sample.mask)
        return stat_func(sample, error)
    return stat_func(sample)
