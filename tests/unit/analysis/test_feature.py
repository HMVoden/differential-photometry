import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.pandas import series
from hypothesis.strategies import floats
from shutterbug.analysis.feature import IQR, InverseVonNeumann


@given(
    series(
        elements=floats(
            min_value=-20,
            max_value=20,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=False,
        )
    )
)
def test_ivn(data):
    if len(data) < 2:
        with pytest.raises(ValueError):
            InverseVonNeumann()(data)
    else:
        result = InverseVonNeumann()(data)
        assert isinstance(result, float)


@given(
    series(
        elements=floats(
            min_value=-20,
            max_value=20,
            allow_nan=False,
            allow_infinity=False,
            allow_subnormal=False,
        )
    )
)
def test_iqr(data):
    result = IQR()(data)
    assert isinstance(result, float)
