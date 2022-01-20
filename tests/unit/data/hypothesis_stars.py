import string

from hypothesis.extra.dateutil import timezones
from hypothesis.strategies import composite, datetimes, floats, integers, lists, text
from shutterbug.data.star import Star, StarTimeseries


@composite
def stars(draw, name: str = None, dataset: str = "test", allow_nan=None) -> Star:

    if name is None:
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
    )
    star.data = timeseries
    return star
