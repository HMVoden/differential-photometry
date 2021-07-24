import logging
from typing import List

import shutterbug.data.utilities as data_util
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
    mag_mean = ds["mag"].groupby("star").mean(...)
    dmag_mean = ds["average_diff_mags"].groupby("star").mean(...)
    mag_day_mean = ds["mag"].groupby("time.date").mean(...)
    dmag_day_mean = ds["average_diff_mags"].groupby("time.date").mean(...)

    mag_day_offset = (mag_mean - mag_day_mean).transpose()
    dmag_day_offset = (dmag_mean - dmag_day_mean).transpose()
    ds = ds.assign(
        {
            "mag_offset": (["time.date", "star"], mag_day_offset),
            "dmag_offset": (["time.date", "star"], dmag_day_offset),
        }
    )
    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.

    # Median of offsets to prevent huge outliers from mucking with data
    # rename so merge doesn't go wonky

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
