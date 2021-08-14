import functools
import logging
from typing import Dict, List

import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype
import shutterbug.ux.progress_bars as bars

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
                "Variable '%s' is not the proper type, attempting to fix", da.name
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
    ds = ds.set_index(timestar=["time", "star"])

    def drop(ds: xr.Dataset):
        ds = ds.drop_duplicates("timestar")
        return ds

    bars.xarray(
        name="dup", desc="Duplicate", unit="variables", indentation=1, leave=False
    )
    ds = ds.progress_map(drop)
    ds = ds.reset_index("timestar", drop=False)
    ds = ds.swap_dims({"timestar": "index"})
    return ds


def clean_data(ds: xr.Dataset, coord_names: List[str]):
    logging.info("Ensuring data is in correct types")
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


# TODO compose this and next function
def remove_incomplete_stars(
    ds: xr.Dataset, stars_to_remove: list[str] = None
) -> xr.Dataset:
    original_stars = np.unique(ds["star"].values)
    nan_stars = find_nan_stars(ds)
    count_stars = find_wrong_count_stars(ds)
    stars_to_remove = functools.reduce(
        np.union1d, [nan_stars, count_stars, stars_to_remove]
    )
    logging.info("Removing specified stars")
    ds = remove_stars(ds, stars_to_remove)
    removed_stars = np.setdiff1d(original_stars, ds["star"].values)
    logging.info("Total removed stars: %s ", len(removed_stars))
    logging.debug("Removed stars with names: %s", removed_stars)
    return ds


def remove_incomplete_time(ds: xr.Dataset) -> xr.Dataset:
    count_time = find_wrong_count_time(ds)
    ds = remove_time(ds, count_time)
    return ds


# TODO make this and next into one function
def find_wrong_count_stars(ds: xr.Dataset) -> list[str]:
    bad_stars = np.array([])
    star_counts = ds.mag.groupby("star").count()
    mode_index = star_counts.idxmax()
    mode = star_counts.sel(star=mode_index)
    bad_stars = xr.where(star_counts == mode, np.NaN, 1).dropna("star").star.values
    # stars, counts = np.unique(ds["star"], return_counts=True)
    # star_mode = np.amax(counts)
    # bad_stars_indices = np.argwhere((counts != star_mode))
    # bad_stars = stars[bad_stars_indices]
    if len(bad_stars) > 0:
        logging.debug(
            "Stars %s have been found without sufficient amounts of information",
            np.unique(bad_stars),
        )
        logging.warning(
            "%s stars have been found without sufficient amounts of information",
            np.unique(bad_stars).size,
        )
    return bad_stars


def find_wrong_count_time(ds: xr.Dataset) -> list[str]:
    bad_time = np.array([])
    time_counts = ds.mag.groupby("time").count()
    mode_index = time_counts.idxmax()
    mode = time_counts.sel(time=mode_index)
    bad_time = xr.where(time_counts == mode, np.NaN, 1).dropna("time").time.values
    if len(bad_time) > 0:
        logging.debug(
            "Time %s have been found without sufficient amounts of information",
            np.unique(bad_time),
        )
        logging.warning(
            "%s time points have been found without sufficient amounts of information",
            np.unique(bad_time).size,
        )
    return bad_time


def find_index_nan(ds: xr.Dataset) -> npt.NDArray[np.int_]:
    bad_indices = np.array([], dtype=np.int64)
    for variable in ds.variables:
        var_good_indices = ds[variable].dropna("index", "any")
        nan_indices = np.setdiff1d(
            ds[variable].index, var_good_indices.index, assume_unique=True
        )
        bad_indices = np.union1d(bad_indices, nan_indices)
    return bad_indices


def find_nan_stars(ds: xr.Dataset) -> list[str]:
    bad_indices = find_index_nan(ds)
    nan_stars = ds.sel(index=bad_indices)
    nan_list = nan_stars["star"].values.tolist()
    if len(nan_list) > 0:
        logging.debug(
            "Stars %s have been found with junk data", np.unique(nan_list),
        )
        logging.warning(
            "%s stars have been found with junk data", np.unique(nan_list).size,
        )
    return nan_list


# TODO make these into one function
def remove_time(ds: xr.Dataset, time_to_remove: list[str]) -> xr.Dataset:
    good_indices = (
        xr.where(ds.time.isin(time_to_remove), np.NaN, 1).dropna("index").index
    )
    ds = ds.sel(index=good_indices)
    return ds


def remove_stars(ds: xr.Dataset, stars_to_remove: list[str]) -> xr.Dataset:
    good_indices = (
        xr.where(ds.star.isin(stars_to_remove), np.NaN, 1).dropna("index").index
    )
    ds = ds.sel(index=good_indices)
    return ds


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
