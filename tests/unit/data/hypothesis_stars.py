import string
from typing import Sequence, Union

from hypothesis.extra.dateutil import timezones
from hypothesis.strategies import composite, datetimes, floats, integers, lists, text
from hypothesis.strategies._internal.strategies import SearchStrategy
from shutterbug.data.star import Star, StarTimeseries


@composite
def star(draw, name: str = "", dataset: str = "test", allow_nan=None) -> Star:

    if not name:
        allowed_names = string.printable
        name = draw(text(alphabet=allowed_names, min_size=1))
    mag = draw(lists(floats(allow_nan=allow_nan), min_size=1))
    error = draw(
        lists(
            floats(allow_nan=allow_nan, min_value=0),
            min_size=len(mag),
            max_size=len(mag),
        )
    )

    time = draw(
        lists(
            datetimes(
                allow_imaginary=False,
                timezones=timezones(),
            ),
            min_size=len(mag),
            max_size=len(mag),
            unique=True,
        )
    )
    timeseries = StarTimeseries(time=time, mag=mag, error=error)
    star = Star(
        dataset=dataset,
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
    dataset: str = "test",
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
        stars.append(draw(star(name=name, dataset=dataset, allow_nan=allow_nan)))
    return stars
