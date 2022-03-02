from decimal import Decimal
import string
from typing import Sequence, Union
from hypothesis import assume
from hypothesis.strategies import (
    composite,
    decimals,
    floats,
    integers,
    lists,
    text,
    DrawFn,
)
from hypothesis.strategies._internal.strategies import SearchStrategy
from shutterbug.data.star import Star, StarTimeseries
import numpy as np
import pandas as pd

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
def star(draw, name: str = "", allow_nan=False) -> Star:

    if not name:

        allowed_names = string.ascii_letters + string.digits
        name = draw(text(alphabet=allowed_names, min_size=1))
    mag = draw(
        lists(floats(allow_nan=allow_nan, allow_infinity=False, width=32), min_size=1)
    )
    assume(not np.isnan(mag).all())
    error = draw(
        lists(
            floats(allow_nan=allow_nan, allow_infinity=False, min_value=0, width=32),
            min_size=len(mag),
            max_size=len(mag),
        )
    )

    time = draw(
        lists(julian_dates(), min_size=len(mag), max_size=len(mag), unique=True)
    )
    frame = pd.DataFrame(
        columns={"magnitude": mag, "error": error}, index=pd.DatetimeIndex(time)
    )
    timeseries = StarTimeseries(data=frame)
    star = Star(
        name=name,
        x=draw(integers(min_value=0, max_value=4096)),
        y=draw(integers(min_value=0, max_value=4096)),
        timeseries=timeseries,
    )
    return star


@composite
def stars(
    draw,
    alphabet: Union[Sequence[str], SearchStrategy[str]],
    min_size=0,
    max_size=None,
    allow_nan=None,
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
