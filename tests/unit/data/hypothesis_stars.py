import string

from hypothesis import given
from hypothesis.strategies import (composite, datetimes, floats, integers,
                                   lists, text)
from shutterbug.data.core.star import Star, StarTimeseries


@composite
def stars(draw, name: str = None, dataset: str = "test", allow_nan=None) -> Star:
    JULIAN_DATE_START_TIME = 2415021.3233796
    JULIAN_DATE_STOP_TIME = 2561118.3233796
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
    # Julian date
    time = draw(
        lists(
            floats(
                allow_nan=allow_nan,
                min_value=JULIAN_DATE_START_TIME,
                max_value=JULIAN_DATE_STOP_TIME,
            ),
            min_size=len(mag),
            max_size=len(mag),
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
