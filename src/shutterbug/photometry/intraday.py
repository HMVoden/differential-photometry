import logging
from typing import Dict, Tuple

import numpy as np
import numpy.typing as npt
import shutterbug.stats.stats as stats
import xarray as xr
from xarray.core.groupby import DatasetGroupBy


def expanding_star_search(
    ds: xr.Dataset,
    radius: float,
    mag_tol: float,
    max_iter: int,
    target: str,
    minimum_stars: int = 20,
    tol_increment: float = 1.0,
) -> Tuple[npt.NDArray, float]:
    """Starting at an initial distance, finds nearby stars. If not enough stars are
    found, determined by minimum stars, expands the search. If unable to find
    enough stars, this will error out.

        Parameters
        ----------
        ds : xr.Dataset
            Clean dataset with x-y coordinates and stars
        radius : float
            initial radius around star to search in a circle
        mag_tol : float
            value to add to magnitude to determine the limit of dimness that we are
            willing to go to for each star
        max_iter : int
            number of radius expansions
        target : str
            target star
        minimum_stars : int
            minimum number of stars to return, errors if not met
        tol_increment : float
            radius increase on each iteration

        Returns
        -------
        Tuple[npt.NDArray, float]
            numpy array of all stars found and the radius they were found in

        Raises
        ------
        RuntimeError
            If not enough stars are found, then this star will break differential
            photometry and thus the program cannot continue without its removal.

    """
    kd_tree = build_kd_tree(ds["x"].values, ds["y"].values)
    mag_stars = find_stars_by_magnitude(ds, mag_tol, target)
    if mag_stars.size <= minimum_stars:
        logging.warning(
            "For star %s not enough stars met magnitude criteria. Using all non-varying stars",
            target,
        )
        return (ds.star.values, radius)

    matching_stars = np.array([])  # so linter doesn't complain
    for i in range(max_iter):
        d_tol = radius + (tol_increment * i)
        nearby_stars = find_nearby_stars(
            ds=ds, tree=kd_tree, tolerance=d_tol, target=target
        )
        matching_stars = np.intersect1d(mag_stars, nearby_stars, assume_unique=True)
        if matching_stars.size >= minimum_stars:  # no more work required
            radius = d_tol
            break
        elif i == (max_iter - 1):
            raise RuntimeError(
                """Unable to find minimum number of stars with set distance and magnitude
                requirements, exiting program"""
            )
    return (matching_stars, radius)


def dataset_differential_photometry(groups: DatasetGroupBy) -> xr.Dataset:
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
        ds = dataset_differential_photometry(ds.groupby(varying_flag))
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
