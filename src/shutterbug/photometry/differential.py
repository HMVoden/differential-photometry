import logging
from typing import Dict

import numpy as np
import scipy.spatial
import shutterbug.photometry.math as math
import shutterbug.progress_bars as bars
import shutterbug.stats.stats as stats
import xarray as xr
from xarray.core.groupby import DatasetGroupBy


def find_nearby_stars(ds: xr.Dataset, tolerance: float, star: str):
    pass


def find_magnitude_stars(ds: xr.Dataset, max: int, min: int) -> xr.Dataset:
    pass


def expanding_star_search(ds: xr.Dataset):
    pass


def calculate_differential_photometry(groups: DatasetGroupBy) -> xr.Dataset:
    if len(groups) == 1:
        # non-varying only
        non_varying = groups[False]
        dm, _ = math.differential_magnitude(non_varying["mag"].values)
        de, _ = math.differential_error(non_varying["error"].values)
        non_varying = non_varying.assign(
            {
                "average_diff_mags": (
                    ["time", "star"],
                    dm,
                ),
                "average_uncertainties": (
                    ["time", "star"],
                    de,
                ),
            }
        )
        return non_varying
    else:
        non_varying = groups[False]

        varying = groups[True]

        dm, vdm = math.differential_magnitude(
            non_varying["mag"].values, varying["mag"].values
        )
        de, vde = math.differential_error(
            non_varying["error"].values, varying["error"].values
        )
        non_varying = non_varying.assign(
            {
                "average_diff_mags": (
                    ["time", "star"],
                    dm,
                ),
                "average_uncertainties": (
                    ["time", "star"],
                    de,
                ),
            }
        )
        varying = varying.assign(
            {
                "average_diff_mags": (
                    ["time", "star"],
                    vdm,
                ),
                "average_uncertainties": (
                    ["time", "star"],
                    vde,
                ),
            }
        )

    return xr.concat([non_varying, varying], dim="star", join="outer")


@bars.progress(
    name="iterations",
    desc="Variable star detection iterations",
    unit="iteration",
    leave=False,
    status_str="Differential Photometry per day",
    indentation=2,
    countable_var="iterations",
    arg_pos=5,
)
def iterate_differential_photometry(
    ds: xr.Dataset,
    method: str = "chisquared",
    p_value: int = 4,
    null="accept",
    clip=False,
    iterations=1,
    pbar_method=None,
    varying_flag="varying",
) -> xr.Dataset:
    logging.info("Processing day %s", ds["time.date"].values[0])
    pbar = bars.get("iterations")
    for i in range(0, iterations, 1):
        # Step 1, get average differential
        ds = calculate_differential_photometry(ds.groupby(varying_flag))
        # Step 2, remove varying and method columns for recalculation
        # ignore errors if columns aren't present
        # Step 3, find varying stars via average differential
        ds.coords[method] = xr.apply_ufunc(
            stats.test_stationarity,
            ds["average_diff_mags"],
            kwargs={"method": method, "clip": clip},
            input_core_dims=[["time"]],
            vectorize=True,
        )
        if null == "accept":
            ds.coords[varying_flag] = ds[method] >= p_value
        else:
            ds.coords[varying_flag] = ds[method] <= p_value

        logging.info(
            "Iteration %s found %s varying stars",
            i + 1,
            ds["intra_varying"].sum().data,
        )
        pbar.update()
    if pbar_method is not None:
        pbar_method()
    bars.close("iterations")

    return ds


@bars.progress(
    name="intra_diff",
    desc="Calculating and finding variable intra-day stars",
    unit="day",
    leave=False,
    status_str="Differential Photometry per day",
    indentation=1,
)
def intra_day_iter(
    ds: xr.Dataset,
    varying_flag: str,
    app_config: Dict,
    method: str,
    iterations: int,
) -> xr.Dataset:
    intra_pbar = bars.get(
        name="intra_diff",
    )
    bars.update(
        pbar=intra_pbar, attr="total", update_to=len(np.unique(ds["time.date"]))
    )
    logging.info("Detecting intra-day variable stars...")
    # No stars varying initially, need for organizing
    ds.coords[varying_flag] = ("star", np.full(ds["star"].size, False))
    ds = ds.groupby("time.date", restore_coord_dims=True, squeeze=False).map(
        iterate_differential_photometry,
        method=method,
        iterations=iterations,
        pbar_method=intra_pbar.update,
        **app_config[method],
        varying_flag=varying_flag,
    )
    ds[varying_flag] = ds[varying_flag].groupby("star").any(...)
    logging.info(
        "Detected total of %s intra-day varying stars",
        ds[varying_flag].sum(...).values,
    )
    return ds


def inter_day(ds: xr.Dataset, app_config: Dict, method: str) -> xr.Dataset:
    clip = app_config[method]["clip"]
    status = bars.status
    status.update(stage="Differential Photometry per star")

    # TODO Throw in callback function for inter_pbars
    inter_pbar = bars.start(
        name="inter_diff",
        total=len(ds.indexes["star"]),
        desc="  Calculating and finding variable inter-day stars",
        unit="Days",
        color="blue",
        leave=False,
    )
    # Detecting if stars are varying across entire dataset
    logging.info("Detecting inter-day variable stars...")
    ds.coords[method] = xr.apply_ufunc(
        stats.test_stationarity,
        (ds["average_diff_mags"].groupby("time.date") - ds["dmag_offset"]),
        kwargs={"method": method, "clip": clip},
        input_core_dims=[["time"]],
        vectorize=True,
    )
    inter_pbar.update(len(ds.indexes["star"]))
    p_value = app_config[method]["p_value"]
    null = app_config[method]["null"]
    if null == "accept":
        ds.coords["inter_varying"] = ds[method] >= p_value
    else:
        ds.coords["inter_varying"] = ds[method] <= p_value
    logging.info(
        "Detected %s inter-day variable stars",
        ds["inter_varying"].groupby("star").all(...).sum(...).data,
    )
    return ds
