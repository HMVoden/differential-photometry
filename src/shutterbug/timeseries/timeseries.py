import logging
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
from astropy.stats import sigma_clip


def correct_offset(ds: xr.Dataset) -> xr.Dataset:

    logging.info("Calculating offset for each star")

    mag_true = ds["mag"].groupby("star").median("time")
    dmag_true = ds["average_diff_mags"].groupby("star").median("time")
    mag_day = ds["mag"].groupby("time.date").median("star")
    dmag_day = ds["average_diff_mags"].groupby("time.date").median("star")

    ds["mag_offset"] = mag_true - mag_day
    ds["dmag_offset"] = dmag_true - dmag_day
    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.
    return ds


def sigma_clip_data(
    data: List[float], stat_func, error: List[float] = None
) -> pd.DataFrame:

    sample = sigma_clip(data, sigma=3, masked=True)
    if error is not None:
        error = np.ma.array(error, mask=sample.mask)
        return stat_func(sample, error)
    return stat_func(sample)
