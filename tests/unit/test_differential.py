from hypothesis.strategies._internal.numbers import floats
from shutterbug.differential import (
    average_differential,
    _average_difference,
    _average_error,
)
from hypothesis import given
from hypothesis.strategies import text
from hypothesis.extra.pandas import column, data_frames
from hypothesis.extra.numpy import datetime64_dtypes
import string


@given(
    data_frames(
        columns=[
            column(
                name="name", elements=text(alphabet=string.ascii_letters, min_size=1)
            ),
            column(
                name="mag",
                elements=floats(
                    min_value=-5, max_value=20, allow_nan=False, allow_infinity=False
                ),
            ),
            column(
                name="error",
                elements=floats(
                    min_value=0, max_value=20, allow_nan=False, allow_infinity=False
                ),
            ),
            column(name="time", elements=datetime64_dtypes(), unique=False),
        ]
    )
)
def test_photometry(stars):
    stars = stars.set_index(["name", "time"])
    for name, star_df in stars.groupby("name"):
        reference = stars.drop(name, level="name")
        adm_ade = average_differential(
            star_df, reference, data_column="mag", error_column="error"
        )
