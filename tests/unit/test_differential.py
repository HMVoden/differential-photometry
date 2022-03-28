import string
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from hypothesis import given
from hypothesis.strategies import (DrawFn, composite, datetimes, floats,
                                   integers, lists, text)
from shutterbug.data.star import Star, StarTimeseries
from shutterbug.differential import average_differential


@composite
def spaced_time(
    draw: DrawFn, space: int = 60, min_size: int = 1, max_size: Optional[int] = None
):
    td = timedelta(seconds=space)
    start = draw(
        datetimes(
            allow_imaginary=False,
            max_value=datetime(2200, month=1, day=1),
            min_value=datetime(1972, month=1, day=1),
        )
    )
    result = [start]
    if max_size is None:
        max_size = draw(integers(min_value=1, max_value=20))
    for i in range(1, max_size):
        result.append(start + (td * i))
    return result


@composite
def timeseries_stars(
    draw: DrawFn,
    min_stars: int = 2,
    max_stars: Optional[int] = None,
    min_entries: int = 1,
    max_entries: Optional[int] = None,
    timeseries_delta: int = 60,
):
    # stars in dataframe
    names = draw(
        lists(
            text(alphabet=string.ascii_letters, min_size=1, max_size=5),
            min_size=min_stars,
            max_size=max_stars,
            unique=True,
        )
    )
    # number of timeseries entries
    num_timeseries = draw(integers(min_value=min_entries, max_value=max_entries))
    ts = draw(
        spaced_time(
            space=timeseries_delta, min_size=num_timeseries, max_size=num_timeseries
        )
    )
    stars = []
    index = pd.to_datetime(ts, utc=True)
    index.name = "time"
    for name in names:
        mag = draw(
            lists(
                floats(
                    min_value=-20, max_value=20, allow_nan=False, allow_infinity=False
                ),
                min_size=num_timeseries,
                max_size=num_timeseries,
            )
        )
        error = draw(
            lists(
                floats(
                    min_value=0, max_value=20, allow_nan=False, allow_infinity=False
                ),
                min_size=num_timeseries,
                max_size=num_timeseries,
            )
        )
        df = pd.DataFrame(index=index, data={"magnitude": mag, "error": error})
        timeseries = StarTimeseries(data=df)
        star = Star(name=name, x=0, y=0, timeseries=timeseries)
        stars.append(star)
    return stars


@given(timeseries_stars(min_stars=2, max_stars=3, max_entries=3))
def test_photometry(stars):
    target = stars[0]
    reference = stars[1:]
    mod_target = average_differential(target, reference)
    assert len(mod_target.timeseries.differential_magnitude) == len(
        target.timeseries.magnitude
    )
    assert len(mod_target.timeseries.differential_error) == len(target.timeseries.error)
