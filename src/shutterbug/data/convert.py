import logging
from typing import List

import numpy as np
import pandas as pd
import xarray as xr


def arrange_star_time(ds: xr.Dataset):
    ds = ds.sortby("time", "star")
    ds = (
        ds.assign_coords(star=np.unique(ds["star"]), time=np.unique(ds["time"]))
        .stack(dim=("time", "star"))
        .reset_index("index", drop=True)
        .rename(dim="index")
        .unstack("index")
    )
    ds.attrs["total_samples"] = ds["star"].size
    ds.attrs["total_stars"] = ds["time"].size
    ds["x"] = ("star", ds["x"].values[0])
    ds["y"] = ("star", ds["y"].values[0])

    return ds


def time_from_column(jd: List[float]) -> pd.DatetimeIndex:
    time = pd.to_datetime(jd, origin="julian", unit="D")
    unique_years = time.year.nunique()
    unique_months = time.month.nunique()
    unique_days = time.day.nunique()

    logging.info("Number of days found in dataset: %s", unique_days)
    logging.info("Number of months found in dataset: %s", unique_months)
    logging.info("Number of years found in dataset: %s", unique_years)

    return time


def add_time(ds: xr.Dataset, time_name):
    ds.coords["time"] = ("index", time_from_column(ds[time_name].values))
    return ds


def add_offset_correction(ds: xr.Dataset) -> xr.Dataset:

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
