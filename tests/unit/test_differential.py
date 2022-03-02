from typing import Optional
from shutterbug.differential import (
    average_differential,
    _average_difference,
    _average_error,
)
from hypothesis import given
from hypothesis.strategies import (
    text,
    composite,
    floats,
    DrawFn,
    lists,
    integers,
    datetimes,
)
from hypothesis.extra.pandas import column, data_frames
from hypothesis.extra.numpy import datetime64_dtypes
import string
import pandas as pd
from datetime import datetime, timedelta, timezone


@composite
def spaced_time(
    draw: DrawFn, space: int = 60, min_size: int = 1, max_size: Optional[int] = None
):
    td = timedelta(seconds=space)
    start = draw(datetimes(allow_imaginary=False))
    result = [start]
    if max_size is None:
        max_size = draw(integers(min_value=1, max_value=20))
    for i in range(1, max_size):
        result.append(start + (td * i))
    return result


@composite
def timeseries_dataframes(
    draw: DrawFn,
    min_stars: int = 2,
    max_stars: Optional[int] = None,
    min_entries: int = 1,
    max_entries: Optional[int] = None,
    timeseries_delta: int = 60,
):
    # stars in dataframe
    stars = draw(
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
    dfs = []
    for name in stars:
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
        index = pd.MultiIndex.from_product([[name], ts], names=["name", "time"])
        df = pd.DataFrame(index=index, data={"mag": mag, "error": error})
        dfs.append(df)

    return pd.concat(dfs)


@given(timeseries_dataframes(max_stars=3, max_entries=3))
def test_photometry(stars):
    stars = stars.sort_index(level="time")
    for name, star_df in stars.groupby("name"):
        reference = stars.drop(name, level="name")
        adm_ade = average_differential(star_df, reference)
