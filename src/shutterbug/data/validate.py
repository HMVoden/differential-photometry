from typing import List

import numpy as np
import numpy.typing as npt

from shutterbug.data.star import StarTimeseries


def validate_timeseries(ts: StarTimeseries) -> StarTimeseries:
    ts.drop_rows(_empty_rows(ts.magnitude, ts.error))
    try:
        assert _is_same_length(ts.magnitude, ts.error)
    except AssertionError:
        raise ValueError("Magnitude and error are not the same length")
    try:
        assert _has_data(ts.magnitude)
        assert _has_data(ts.error)
    except AssertionError:
        raise ValueError("Either magnitude or error has no values")
    return ts


def _has_data(values: npt.NDArray[np.float_]) -> bool:
    if len(values) == 0:
        return False
    values = np.asarray(values)
    return not bool(np.isnan(values).all())


def _is_same_length(*values: npt.NDArray[np.float_]) -> bool:
    if len(values) == 0:
        raise ValueError("Did not receive any data to compare")
    if len(values) == 1:
        return True
    last_length = values[0]
    for v in values[1:]:
        if len(v) != last_length:
            return False
    return True


def _empty_rows(*values: npt.NDArray[np.float_]) -> List[int]:
    stack = np.hstack(values)
    return np.isnan(stack).all(axis=0)
