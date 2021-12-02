import numpy as np
from numpy.typing import NDArray


def clean_nan(data: NDArray[float]) -> NDArray:
    """Removes all NaN entries from given numerical data

    Parameters
    ----------
    data : NDArray[float]
        Array of numbers

    Returns
    -------
    NDArray
        Array of numbers without any NaN

    """

    nan_indices = find_nan(data)
    data = np.delete(data, nan_indices)
    return data


def find_nan(data: NDArray[float]) -> NDArray[int]:
    """Finds all instances of NaN within a numerical dataset

    Parameters
    ----------
    data : NDArray[float]
        Array of numbers

    Returns
    -------
    NDArray[int]
        List of integers corresponding to the indices of any NaN entries in data
    """
    nan_indices = np.argwhere(np.isnan(data))  # slow
    return nan_indices
