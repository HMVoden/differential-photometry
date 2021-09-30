from typing import Any

import numpy as np
from numpy.typing import NDArray


def find_duplicates(*list_data: NDArray[Any]) -> NDArray[int]:
    """Finds duplicates within given dataset

    Using the given axis as the source data, this function finds any duplicate
    of that source data and returns an array of bools that maps to the location
    of the duplicates.

    Parameters
    ----------
    *list_data : NDArray[Any]
        A number of arrays of equal length to test for duplicates

    Returns
    -------
    NDArray[int]
        Array of array of integers, each corresponding to a different set of duplicate indices

    """
    data = zip(*list_data)

    hashmap = {}
    duplicate_indices = []
    for index, row in enumerate(data):
        if row in hashmap:
            hashmap[row].append(index)
        else:
            hashmap[row] = [index]
    for indices in list(hashmap.values()):
        if len(indices) > 1:
            duplicate_indices.append(indices)
    return np.asarray(duplicate_indices)
