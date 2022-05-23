import string
from typing import Sequence, Union

import pandas as pd
from hypothesis.extra.pandas import columns, data_frames
from hypothesis.strategies import (DrawFn, composite, decimals, floats,
                                   integers, lists, text)
from hypothesis.strategies._internal.strategies import SearchStrategy
from shutterbug.data.star import Star, StarTimeseries

DAYS_IN_JULIAN_YEAR = 365.25
UNIX_0_POINT_JD = 2440588.5
END_POINT_JD = UNIX_0_POINT_JD + (DAYS_IN_JULIAN_YEAR * 200)


@composite
def julian_dates(draw: DrawFn) -> float:
    return float(
        draw(
            decimals(
                min_value=UNIX_0_POINT_JD,
                max_value=END_POINT_JD,
                allow_nan=False,
                allow_infinity=False,
                places=3,
            )
        )
    )


@composite
def date_time_indexes(draw: DrawFn, min_size=1, max_size=None):
    return pd.to_datetime(
        draw(lists(julian_dates(), min_size=min_size, max_size=max_size, unique=True)),
        origin="julian",
        unit="D",
        utc=True,
    ).round("1s")


@composite
def timeseries(draw: DrawFn, min_size=1, max_size=None):
    data = draw(
        data_frames(
            columns=columns(
                ["magnitude", "error"],
                elements=floats(min_value=-20, max_value=20, allow_nan=False, width=16),
            ),
            index=date_time_indexes(min_size=min_size, max_size=max_size),
        ),
    )
    ts = StarTimeseries(data=data)
    # Issue with hypothesis caching old features
    # Hard set to empty to fix
    ts._features = {}
    for date in data.index.date:
        ts.add_feature(
            dt=date,
            name="Inverse Von Neumann",
            value=draw(floats(min_value=1, max_value=5)),
        )
        ts.add_feature(
            dt=date,
            name="IQR",
            value=draw(floats(min_value=1, max_value=5)),
        )
    return ts


@composite
def star(draw, name: str = "", allow_nan=False) -> Star:
    if not name:

        allowed_names = string.ascii_letters + string.digits
        name = draw(text(alphabet=allowed_names, min_size=1))
    ts = draw(timeseries(max_size=10))
    star = Star(
        name=name,
        x=draw(integers(min_value=0, max_value=4096)),
        y=draw(integers(min_value=0, max_value=4096)),
        timeseries=ts,
    )
    return star


@composite
def stars(
    draw,
    alphabet: Union[Sequence[str], SearchStrategy[str]],
    min_size=0,
    max_size=None,
    allow_nan=False,
):
    names = draw(
        lists(
            text(alphabet=alphabet, min_size=min_size, max_size=max_size),
            unique=True,
            min_size=min_size,
            max_size=max_size,
        )
    )
    stars = []
    for name in names:
        stars.append(draw(star(name=name, allow_nan=allow_nan)))
    return stars
