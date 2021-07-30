import logging
from typing import Any, Dict, List

import pandas as pd
import xarray as xr
import numpy as np
import shutterbug.data.utilities as util
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
from functools import cache

from natsort import natsorted

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


def drop_duplicates(ds: xr.Dataset):
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

    return ds


def add_time_information(ds: xr.Dataset, time_name):
    ds.coords["time"] = ("index", util.time_from_data(ds[time_name].data))
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
    if "obj" in ds.keys():
        ds = ds.rename(obj="star")
    if "name" in ds.keys():
        ds = ds.rename(name="star")
    return ds


def remove_incomplete_stars(
    ds: xr.Dataset, stars_to_remove: list[str] = None
) -> List[float]:
    stars, counts = np.unique(ds["star"].values, return_counts=True)
    star_mode = np.amax(counts)  # most common value
    bad_stars = np.extract((counts != star_mode), stars).tolist()
    nan_stars = ds.where(ds["mag"].isnull() | ds["error"].isnull(), drop=True)[
        "star"
    ].data.tolist()
    bad_stars.extend(nan_stars)

    if len(bad_stars) > 0:
        logging.warning(
            "Stars %s have been found without sufficient amount of information",
            np.unique(bad_stars),
        )
    if stars_to_remove is not None:
        bad_stars.extend(stars_to_remove)
    ds = ds.where(~ds["star"].isin(bad_stars), drop=True)
    bad_stars = np.unique(bad_stars)
    logging.info("Removed stars: %s", bad_stars)
    logging.info("Removed star count %s", len(bad_stars))
    return ds


def to_remove_to_list(to_remove: str) -> List[str]:
    if to_remove is not None:
        if "," in to_remove:
            to_remove.str.replace(" ", "")
            to_remove = to_remove.split(",")
        else:
            to_remove = to_remove.split(" ")
    else:
        to_remove = []
    return to_remove


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
