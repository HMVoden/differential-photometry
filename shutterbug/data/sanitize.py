import logging
from typing import Any, Dict, List

import pandas as pd
import xarray as xr
import numpy as np
import shutterbug.data.utilities as util
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

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
        if name != new_name:
            from_to[name] = new_name
    return from_to


def drop_duplicates(da: xr.DataArray):
    da = da.set_index(time_star=("time", "star"))
    da = da.drop_duplicates("time_star")
    da = da.reset_index("time_star")
    da = da.swap_dims({"time_star": "star"})
    return da


def clean_data(ds: xr.Dataset, coord_names: List[str], time_name: str):
    logging.info("Cleaning data")
    ds = ds.set_coords(coord_names)
    ds = ds.swap_dims({"index": "star"})
    ds = ds.drop_vars(["index"])
    ds = ds.map(check_and_coerce_dataarray)
    time = util.time_from_data(ds[time_name].values)
    ds.coords["time"] = ("star", time)
    logging.info("Dropping duplicate entries")
    ds = ds.map(drop_duplicates)
    logging.info("Cleaned data")
    return ds


def arrange_data(ds: xr.Dataset) -> xr.Dataset:
    ds.attrs["total_samples"] = len(np.unique(ds["time"]))
    ds.attrs["total_stars"] = len(np.unique(ds["star"]))
    arranged = util.arrange_time_star(
        ds.attrs["total_samples"],
        ds.attrs["total_stars"],
        ds["mag"],
        ds["error"],
        ds["x"],
        ds["y"],
    )
    # Rebuild dataset so we can have proper dimensions. Can't figure out how to
    # set dimensions or re-shape in-xr dataset
    ds = xr.Dataset(
        data_vars={
            "mag": (
                ["time", "star"],
                next(arranged),
            ),
            "error": (
                ["time", "star"],
                next(arranged),
            ),
        },
        coords={
            "jd": ("time", np.unique(ds["jd"])),
            "x": ("star", next(arranged)[0]),
            "y": ("star", next(arranged)[0]),
            "time": ("time", np.unique(ds["time"])),
            "star": ("star", np.unique(ds["star"])),
        },
        attrs=ds.attrs,
    )
    return ds


def drop_and_clean_names(ds: xr.Dataset, required_data: List[str]) -> xr.Dataset:
    cleaned = clean_names(ds.keys())
    to_drop = []
    for name, clean_name in cleaned.items():
        if clean_name not in required_data:
            to_drop.append(name)
    for name in to_drop:
        cleaned.pop(name, None)
    ds = ds.drop_vars(to_drop)
    ds = ds.rename(cleaned)
    try:
        ds = ds.rename(obj="star")
    except ValueError:
        pass
    try:
        ds = ds.rename(name="star")
    except ValueError:
        pass
    return ds


def remove_incomplete_sets(
    ds: xr.Dataset, stars_to_remove: list[str] = None
) -> List[float]:
    """Founds the most common row counts by virtue of the star names in the dataset
    then removes any stars that do not have the same amount as the most common row count

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to be cleaned, must contain "id" column

    Returns
    -------
    pd.DataFrame
        Dataframe cleaned
    """
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
    )
    # Cleanup of headers, could be made more succinct with a simple REGEX or two

    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this function.
    # Finds common column names
    return header
