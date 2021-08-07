import logging
from functools import cache
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import shutterbug.data.utilities as util
import xarray as xr
from natsort import natsorted
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
from scipy.stats import mode

columns_check_function = {
    "mag": is_numeric_dtype,
    "error": is_numeric_dtype,
    "time": is_datetime64_any_dtype,
}

columns_fix_function = {
    "mag": pd.to_numeric,
    "error": pd.to_numeric,
    "time": pd.to_datetime,
}


def check_and_coerce_dataarray(da: xr.DataArray) -> xr.DataArray:
    if da.name in columns_check_function.keys():
        if not columns_check_function[da.name](da.values):
            logging.warning(
                "Data column '%s' is not the proper type, attempting to fix", da.name
            )
            da.values = columns_fix_function[da.name](da.values, errors="coerce")
    return da


def clean_names(names: List[str]) -> Dict:
    from_to = {}
    for name in names:
        new_name = clean_header(name)
        from_to[name] = new_name
    return from_to


def drop_duplicate_time(ds: xr.Dataset):
    logging.info("Removing duplicates")
    ds = ds.swap_dims({"index": "time"})

    def drop(ds: xr.Dataset):
        ds = ds.map(lambda x: x.drop_duplicates("time"))
        return ds

    ds = ds.groupby("star").map(drop)
    ds = ds.swap_dims({"time": "index"})
    return ds


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


def clean_data(ds: xr.Dataset, coord_names: List[str]):
    logging.info("Cleaning data")
    ds = ds.set_coords(coord_names)
    ds = ds.map(check_and_coerce_dataarray)
    return ds


def drop_and_clean_names(ds: xr.Dataset, required_data: List[str]) -> xr.Dataset:
    cleaned = clean_names(list(ds.keys()))
    to_drop = []
    for name, clean_name in cleaned.items():
        if clean_name not in required_data:
            to_drop.append(name)
    for name in to_drop:
        cleaned.pop(name, None)
    ds = ds.drop_vars(to_drop)
    ds = ds.rename(cleaned)
    if "name" in ds.keys():
        ds = ds.rename(name="star")
    return ds


def remove_incomplete_stars(
    ds: xr.Dataset, stars_to_remove: list[str] = None
) -> xr.Dataset:
    logging.info("Removing stars")
    original_stars = np.unique(ds["star"].values)
    ds = ds.pipe(remove_nan_stars).pipe(remove_wrong_count_stars)
    if stars_to_remove is not None:
        ds = remove_stars(ds, stars_to_remove)
    removed_stars = np.setdiff1d(original_stars, ds["star"].values)
    logging.info("Total removed stars: %s ", len(removed_stars))
    logging.debug("Removed stars with names: %s", removed_stars)
    return ds


def remove_wrong_count_stars(ds: xr.Dataset):
    stars, counts = np.unique(ds["star"], return_counts=True)
    mode_list, _ = mode(counts, axis=None)
    star_mode = mode_list[0]
    bad_stars = np.extract((counts != star_mode), stars).tolist()
    ds = remove_stars(ds, bad_stars)
    if len(bad_stars) > 0:
        logging.warning(
            "Stars %s have been found without sufficient amount of information",
            np.unique(bad_stars),
        )
    return ds


def remove_nan_stars(ds: xr.Dataset):
    nan_stars = ds.where(ds.isnull(), drop=True)
    nan_list = nan_stars["star"].values.tolist()
    if len(nan_list) > 0:
        logging.warning(
            "Stars %s have been found with junk data",
            np.unique(nan_list),
        )
    ds = remove_stars(ds, nan_list)
    return ds


def remove_stars(ds: xr.Dataset, stars_to_remove: list[str]):
    removal_index_array = ~ds["star"].isin(stars_to_remove)
    ds = ds.where(removal_index_array, drop=True)
    return ds


def to_remove_to_list(to_remove: str = None) -> List[str]:
    result = []
    if to_remove is not None:
        if "," in to_remove:
            to_remove = to_remove.replace(" ", "")
            result = to_remove.split(",")
        else:
            result = to_remove.split(" ")
    return result


def clean_header(header: str) -> str:
    header = (
        header.strip()
        .lower()
        .replace(" ", "_")
        .replace("(", "_")
        .replace(")", "")
        .replace("<", "")
        .replace(">", "")
        .replace("?", "")
        .replace("/", "-")
    )
    # Cleanup of headers, could be made more succinct with a simple REGEX or two

    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this function.
    # Finds common column names
    return header


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
