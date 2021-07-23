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


def check_and_coerce_column(data: List[Any]) -> List[Any]:
    if data.name in columns_check_function.keys():
        if not columns_check_function[data.name](data.values):
            logging.warning(
                "Data column '%s' is not the proper type, attempting to fix", data.name
            )
            data = columns_fix_function[data.name](data, errors="coerce")
    return data


def clean_names(names: List[str]) -> Dict:
    from_to = {}
    for name in names:
        new_name = clean_header(name)
        if name != new_name:
            from_to[name] = new_name
    return from_to


def clean_data(ds: xr.Dataset, coord_names: List[str], time_name: str):
    logging.info("Cleaning data")
    ds = ds.apply(check_and_coerce_column)
    ds = ds.set_coords(coord_names)
    time = util.time_from_data(ds[time_name].values)
    ds["time"] = time
    ds["star"] = np.unique(ds["star"])
    ds.attrs["samples"] = time.nunique()
    ds.attrs["stars"] = int(ds.dims["index"] / time.nunique())
    return ds


def arrange_data(ds: xr.Dataset) -> xr.Dataset:
    num_stars = ds.attrs["stars"]
    num_samples = ds.attrs["samples"]
    arranged = util.arrange_time_star(
        num_stars, num_samples, ds["mag"], ds["error"], ds["x"], ds["y"]
    )
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
            "time": ("time", ds["time"]),
            "star": ("star", natsorted(ds["star"].values)),
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

    if len(bad_stars) > 0:
        logging.warning(
            "Stars %s have been found without sufficient amount of information",
            bad_stars,
        )
    if stars_to_remove is not None:
        bad_stars.extend(stars_to_remove)

    ds = ds.where(~ds["star"].isin(bad_stars), drop=True)

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
