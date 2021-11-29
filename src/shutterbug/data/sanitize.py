import functools
import logging
from typing import Dict, List

import numpy as np
import numpy.typing as npt
import pandas as pd
import shutterbug.ux.progress_bars as bars
import xarray as xr
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


def check_and_coerce_dataarray(ds: xr.Dataset) -> xr.Dataset:
    for variable in ds.variables.keys():
        if variable in columns_check_function.keys():
            ds[variable] = (
                "index",
                columns_fix_function[variable](ds[variable].data, errors="coerce"),
            )
    return ds


def clean_names(names: List[str]) -> Dict:
    from_to = {}
    for name in names:
        new_name = clean_header(name)
        from_to[name] = new_name
    return from_to


def drop_duplicate_time(ds: xr.Dataset):
    logging.info("Removing duplicates")
    factorized_stars = pd.factorize(ds.star.data)[0]
    factorized_time = pd.factorize(ds.time.data)[0]
    time_star = np.column_stack((factorized_stars, factorized_time))
    _, indices = np.unique(time_star, return_index=True, axis=0)
    good_indices = ds.index.data[indices]
    ds = ds.sel(index=good_indices)
    return ds


def clean_data(ds: xr.Dataset, coord_names: List[str]):
    logging.info("Ensuring data is in correct types")
    ds = ds.set_coords(coord_names)
    ds = ds.pipe(check_and_coerce_dataarray)
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
<<<<<<< HEAD
=======
    if "obj" in ds.keys():
        ds = ds.rename(obj="star")
<<<<<<< HEAD:src/shutterbug/data/sanitize.py
>>>>>>> main
    if "name" in ds.keys():
=======
    if "name"  in ds.keys():
>>>>>>> 14fa39af25ec1544244fc9637b3cec17f30b372f:shutterbug/data/sanitize.py
        ds = ds.rename(name="star")
    return ds


# TODO compose this and next function
def remove_incomplete_stars(
    ds: xr.Dataset, stars_to_remove: list[str] = None
) -> xr.Dataset:
    original_stars = np.unique(ds["star"].data)
    nan_stars = find_nan_stars(ds)
    count_stars = find_wrong_count_stars(ds)
    stars_to_remove = functools.reduce(
        np.union1d, [nan_stars, count_stars, stars_to_remove]
    )
    logging.info("Removing stars")
    ds = remove_stars(ds, stars_to_remove)
    removed_stars = np.setdiff1d(original_stars, ds["star"].data)
    logging.info("Total removed stars: %s ", len(removed_stars))
    logging.debug("Removed stars with names: %s", removed_stars)
    return ds


def remove_incomplete_time(ds: xr.Dataset) -> xr.Dataset:
    count_time = find_wrong_count_time(ds)
    logging.info("Removing time")
    ds = remove_time(ds, count_time)
    return ds


# TODO make this and next into one function
def find_wrong_count_stars(ds: xr.Dataset) -> list[str]:
    stars, counts = np.unique(ds["star"], return_counts=True)
    star_mode, _ = mode(counts)
    bad_stars_indices = np.argwhere((counts != star_mode)).flatten()
    bad_stars = stars[bad_stars_indices]
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
    time, counts = np.unique(ds["time"], return_counts=True)
    time_mode, _ = mode(counts)
    bad_time_indices = np.argwhere((counts != time_mode)).flatten()
    bad_time = time[bad_time_indices]
    if len(bad_time) > 0:
        logging.debug(
            "Time %s have been found without sufficient amounts of information",
            np.unique(bad_time),
        )
        logging.warning(
            "%s time points have been found without sufficient amounts of information",
            np.unique(bad_time).size,
        )
    return bad_time.flatten()


def find_index_nan(ds: xr.Dataset) -> npt.NDArray[np.int_]:
    bad_indices = np.array([], dtype=np.int64)
    for variable in ds.variables:
        nan_raw_indices = np.flatnonzero(ds[variable].isnull().data)

        nan_ds_indices = ds.index[nan_raw_indices]
        bad_indices = np.union1d(bad_indices, nan_ds_indices)
    return bad_indices


def find_nan_stars(ds: xr.Dataset) -> list[str]:
    bad_indices = find_index_nan(ds)
    nan_stars = ds.sel(index=bad_indices)
    nan_list = nan_stars["star"].data.tolist()
    if len(nan_list) > 0:
        logging.debug(
            "Stars %s have been found with junk data",
            np.unique(nan_list),
        )
        logging.warning(
            "%s stars have been found with junk data",
            np.unique(nan_list).size,
        )
    return nan_list


# TODO make these into one function
def remove_time(ds: xr.Dataset, time_to_remove: list[str]) -> xr.Dataset:
    time_to_remove = set(time_to_remove)
    bad_indices = np.flatnonzero(
        np.array([(1 if x in time_to_remove else 0) for x in ds.time.data])
    )

    ds = ds.drop_sel(index=ds.index.data[bad_indices])
    return ds


def remove_stars(ds: xr.Dataset, stars_to_remove: list[str]) -> xr.Dataset:
    stars_to_remove = set(stars_to_remove)
    bad_indices = np.flatnonzero(
        np.array([(1 if x in stars_to_remove else 0) for x in ds.star.data])
    )

    ds = ds.drop_sel(index=ds.index.data[bad_indices])
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
