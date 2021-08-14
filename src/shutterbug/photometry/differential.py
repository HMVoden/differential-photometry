import logging
from math import sqrt
from typing import List, Tuple

import numpy as np
import numpy.typing as npt
import xarray as xr
from numba import float32, float64, guvectorize
from xarray.core.groupby import DatasetGroupBy


# def sigma_clip_data(data: List[float], stat_func, error: List[float] = None) -> float:

#     sample = sigma_clip(data, sigma=3, masked=True)
#     if error is not None:
#         error = np.ma.array(error, mask=sample.mask)
#         return stat_func(sample, error)
#     return stat_func(sample)


def magnitude(
    mags: npt.NDArray, varying_mags: npt.NDArray = None,
) -> Tuple[npt.NDArray, npt.NDArray]:
    diff_mag = []
    varying_diff_mag = []
    mags = mags.transpose()
    if varying_mags is not None:
        varying_mags = varying_mags.transpose()
        for star in varying_mags:
            vdm = np.mean((mags - star), axis=0)
            # vdm = average((mags - star), axis=0)
            varying_diff_mag.append(vdm)

    for index, star in enumerate(mags):
        reference = np.delete(mags, index, axis=0)
        dm = np.mean((reference - star), axis=0)
        # dm = average((reference - star), axis=0)

        diff_mag.append(dm)
    diff_mag = np.asanyarray(diff_mag).transpose()
    varying_diff_mag = np.asanyarray(varying_diff_mag).transpose()
    return diff_mag, varying_diff_mag


def error(
    error: npt.NDArray, varying_error: npt.NDArray = None,
) -> Tuple[npt.NDArray, npt.NDArray]:
    diff_error = []
    varying_diff_error = []
    error = error.transpose()
    if varying_error is not None:
        varying_error = varying_error.transpose()
        N = error.shape[0] + 1
        for star in varying_error:
            vde = np.sqrt(np.sum((error ** 2 + star ** 2), axis=0)) / N
            # vde = average_error((error ** 2 + star ** 2), axis=0)
            varying_diff_error.append(vde)
    N = error.shape[0]
    for index, star in enumerate(error):
        reference = np.delete(error, index, axis=0)
        de = np.sqrt(np.sum((error ** 2 + star ** 2), axis=0)) / N
        # de = average_error((reference - star), axis=0)
        diff_error.append(de)
    diff_error = np.asanyarray(diff_error).transpose()
    varying_diff_error = np.asanyarray(varying_diff_error).transpose()
    return diff_error, varying_diff_error


def calculate_differential_magnitude(
    target: npt.NDArray, reference: npt.NDArray
) -> npt.NDArray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_differential_uncertainty(
    target: npt.NDArray, reference: npt.NDArray
) -> npt.NDArray:
    """Calculates a single timeseries differential magnitude uncertainty"""
    return np.sqrt(target ** 2 + reference ** 2)


def data_array_magnitude(target: xr.DataArray, reference: xr.DataArray) -> xr.DataArray:
    return (reference - target).mean("star")


def data_array_uncertainty(
    target: xr.DataArray, reference: xr.DataArray
) -> xr.DataArray:
    N = reference.star.size + target.star.size
    return (reference ** 2 + target ** 2).sum("star") / N


# guvectorize intentionally does not return.
@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average(subtracted_magnitudes: List[float], out: float):
    N = len(subtracted_magnitudes)
    out = 0
    for mag in subtracted_magnitudes:
        out = out + mag
    out = out / N


@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average_error(errors: List[float], out: float):
    N = len(errors)
    out = 0
    for error in errors:
        out = out + error ** 2
    out = sqrt(out) / N


def dataset(groups: DatasetGroupBy) -> xr.Dataset:
    if len(groups) == 1:
        # non-varying only
        non_varying = groups[False]
        dm, _ = magnitude(non_varying["mag"].values)
        de, _ = error(non_varying["error"].values)
        non_varying = non_varying.assign(
            {
                "average_diff_mags": (["time", "star"], dm,),
                "average_uncertainties": (["time", "star"], de,),
            }
        )
        return non_varying
    else:
        non_varying = groups[False]

        varying = groups[True]

        dm, vdm = magnitude(non_varying["mag"].values, varying["mag"].values)
        de, vde = error(non_varying["error"].values, varying["error"].values)
        non_varying = non_varying.assign(
            {
                "average_diff_mags": (["time", "star"], dm,),
                "average_uncertainties": (["time", "star"], de,),
            }
        )
        varying = varying.assign(
            {
                "average_diff_mags": (["time", "star"], vdm,),
                "average_uncertainties": (["time", "star"], vde,),
            }
        )

    return xr.concat([non_varying, varying], dim="star", join="outer")
