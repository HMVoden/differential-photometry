import logging
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
from astropy.stats import sigma_clip


def correct_offset(ds: xr.Dataset) -> xr.Dataset:
    """Finds the offset of an entire timeseries across many days
    by taking the weighted average of every point in timeseries and assuming
    that this is the true mean of the timeseries, then finds the mean of each
    individual day in the timeseries, and brings that to the assumed true mean

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing magnitude and differential magnitude

    Returns
    -------
    pd.DataFrame
        Dataframe where magnitude and differential magnitude have been corrected
    """
    logging.info("Calculating offset for each star")
    mag_true = ds["mag"].groupby("star").median(...)
    dmag_true = ds["average_diff_mags"].groupby("star").median(...)
    mag_day = ds["mag"].groupby("time.date").median(...)
    dmag_day = ds["average_diff_mags"].groupby("time.date").median(...)

    ds["mag_offset"] = mag_true - mag_day
    ds["dmag_offset"] = dmag_true - dmag_day

    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.

    return ds


def sigma_clip_data(
    data: List[float], stat_func, error: List[float] = None
) -> pd.DataFrame:
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
