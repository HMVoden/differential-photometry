from math import sqrt
from typing import List, Tuple

import numpy as np
from numba import float32, float64, guvectorize, jit


def unpack_tuples():
    pass


def differential_magnitude(
    mags: List[List[float]],
    varying_mags: List[List[float]] = None,
) -> Tuple[List[List[float]], List[List[float]]]:
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


def differential_error(
    error: List[List[float]],
    varying_error: List[List[float]] = None,
) -> Tuple[List[List[float]], List[List[float]]]:
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
    target: np.ndarray, reference: np.ndarray
) -> np.ndarray:
    """Calculates a single timeseries differential magnitude"""
    return reference - target


def calculate_differential_uncertainty(
    target: np.ndarray, reference: np.ndarray
) -> np.ndarray:
    """Calculates a single timeseries differential magnitude uncertainty"""
    return np.sqrt(target ** 2 + reference ** 2)


# guvectorize intentionally does not return.
@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average(subtracted_magnitudes: List[float], out: List) -> float:
    N = len(subtracted_magnitudes)
    out = 0
    for mag in subtracted_magnitudes:
        out = out + mag
    out = subtracted_magnitudes / N


@guvectorize([(float32[:], float32), (float64[:], float64)], "(n) -> ()")
def average_error(errors: List[float], out: List) -> float:
    N = len(errors)
    out = 0
    for error in errors:
        out = out + error ** 2
    out = sqrt(out) / N
