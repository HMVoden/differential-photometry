from typing import List, Sequence
import logging
import numpy as np
import numpy.typing as npt


def _has_data(values: npt.NDArray[np.float_]) -> bool:
    """Checks if all values in given sequence are NaN or if there are any values at
    all"""
    if len(values) == 0:
        return False
    values = np.asarray(values)
    return not bool(np.isnan(values).all())


def _is_same_length(*values: Sequence[float]) -> bool:
    """Takes arbitrary number of sequences and checks if they are equal length"""
    if len(values) <= 1:
        return True
    last_length = len(values[0])
    for v in values[1:]:
        if len(v) != last_length:
            return False
    return True


def _empty_rows(*values: Sequence[float]) -> List[int]:
    """Takes an arbitrary number of sequences and finds all rows in those sequences
    that are empty"""
    if not _is_same_length(*values):
        raise ValueError("Input rows not the same length")
    stack = np.hstack(values)
    empties = np.isnan(stack).all(axis=0)
    return empties.nonzero()[0]
