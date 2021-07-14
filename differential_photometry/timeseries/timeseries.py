import logging
from typing import List

import differential_photometry.data.utilities as data_util
import numpy as np
import pandas as pd
from astropy.stats import sigma_clip


def correct_offset(df: pd.DataFrame) -> pd.DataFrame:
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
    non_varying, _ = data_util.split_on(df, "intra_varying")
    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.
    true_mean = non_varying.groupby("id").agg({
        "mag": "mean",
        "average_diff_mags": "mean"
    })
    # Individual day means to find offset
    day_star_mean = non_varying.groupby(["d_m_y", "id"]).agg({
        "mag":
        "mean",
        "average_diff_mags":
        "mean"
    })
    offset = day_star_mean.sub(true_mean, axis="index").reset_index()
    # Median of offsets to prevent huge outliers from mucking with data
    per_day_offset = offset.groupby("d_m_y").mean().reset_index()
    # rename so merge doesn't go wonky
    per_day_offset = per_day_offset.rename(
        columns={
            "mag": "mag_offset",
            "average_diff_mags": "diff_mag_offset"
        })
    df_corrected = df.copy()
    df_corrected = df_corrected.merge(per_day_offset,
                                      left_on="d_m_y",
                                      right_on="d_m_y",
                                      how="inner")
    df_corrected["c_mag"] = df_corrected["mag"] - df_corrected["mag_offset"]
    df_corrected["c_average_diff_mags"] = df_corrected[
        "average_diff_mags"] - df_corrected["diff_mag_offset"]

    return df_corrected


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
