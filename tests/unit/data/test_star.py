import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis.strategies import floats, composite, lists, text, DrawFn, SearchStrategy
from shutterbug.data.star import Star, StarTimeseries
from typing import List, Optional, Tuple, Union

DAYS_IN_JULIAN_YEAR = 365.25
UNIX_0_POINT_JD = 2440588.5
END_POINT_JD = UNIX_0_POINT_JD + (DAYS_IN_JULIAN_YEAR * 200)


@composite
def julian_dates(draw: DrawFn) -> float:
    return draw(
        floats(
            min_value=UNIX_0_POINT_JD,
            max_value=END_POINT_JD,
            allow_nan=False,
            allow_infinity=False,
        )
    )


@composite
def timeseries_row(draw: DrawFn, allow_nan: bool = True) -> List[float]:
    time = draw(julian_dates())
    mag = draw(floats(allow_nan=allow_nan, allow_infinity=False))
    error = draw(floats(allow_nan=allow_nan, allow_infinity=False))
    return [time, mag, error]


@composite
def same_size_lists(
    draw: DrawFn,
    elements: List[SearchStrategy],
    min_size: int = 0,
    max_size: Optional[int] = None,
):
    return_list = [draw(lists(elements[0], min_size=min_size, max_size=max_size))]
    size = len(return_list[0])
    for element in elements[1:]:
        return_list.append(draw(lists(element, min_size=size, max_size=size)))
    return return_list


@given(lists(timeseries_row(allow_nan=False), min_size=1))
def test_timeseries_validation(rows):
    columns = np.asarray(rows)
    ts = StarTimeseries(time=columns[:, 0], mag=columns[:, 1], error=columns[:, 2])
    assert len(np.argwhere(pd.isna(ts.time))) == 0
    assert len(ts.time) == len(ts.error) and len(ts.time) == len(ts.mag)
    assert len(np.unique(ts.time)) == len(ts.time)
    assert ts.nbytes == (ts.time.nbytes + ts.mag.nbytes + ts.error.nbytes)


@given(
    same_size_lists(
        elements=[
            julian_dates(),
            floats(allow_nan=True, allow_infinity=False),
            floats(allow_nan=True, allow_infinity=False),
        ],
        min_size=1,
    )
)
def test_timeseries_bad_data(rows):
    time, mag, error = rows
    time = np.asarray(time)
    mag = np.asarray(mag)
    error = np.asarray(error)
    unique_time, indices = np.unique(time, return_index=True)
    unique_mag = mag[indices]
    unique_error = error[indices]
    if np.isnan(unique_mag).all():
        with pytest.raises(ValueError):
            StarTimeseries(time=unique_time, mag=mag, error=unique_error)
    elif np.isnan(mag).all():
        with pytest.raises(ValueError):
            StarTimeseries(time=time, mag=mag, error=error)
    elif len(np.argwhere(np.isnan(time))) == len(time):
        with pytest.raises(ValueError):
            StarTimeseries(time=time, mag=mag, error=error)
    else:
        ts = StarTimeseries(time=time, mag=mag, error=error)
        unique_times = np.unique(time)
        assert [True if x in ts.time else False for x in unique_times]
