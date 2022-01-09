import string

import numpy as np
import pandas as pd
import pytest
from hypothesis import assume, given
from hypothesis.extra.numpy import arrays, datetime64_dtypes
from hypothesis.strategies import (DrawFn, SearchStrategy, composite, floats,
                                   integers, lists, text)
from pandas.api.types import is_numeric_dtype
from shutterbug.data.core.star import Star, StarTimeseries


@composite
def three_lists(
    draw: DrawFn, elements: SearchStrategy, min_size: int = 0, max_size: int = None
):
    l1 = draw(lists(elements=elements, min_size=min_size, max_size=max_size))
    length = len(l1)
    l2 = draw(lists(elements=elements, min_size=length, max_size=length))
    l3 = draw(lists(elements=elements, min_size=length, max_size=length))
    return l1, l2, l3


@given(lists(floats()), lists(floats()))
def test_insufficient_information_timeseries(l1, l2):
    with pytest.raises(TypeError):
        StarTimeseries(time=l1, mag=l2)  # type: ignore


@given(
    arrays(dtype=datetime64_dtypes(), shape=1, unique=True),
    lists(floats()),
    lists(floats()),
)
def test_different_lengths(l1, l2, l3):
    assume(len(l1) != len(l2))
    assume(len(l1) != len(l3))
    with pytest.raises(AssertionError):
        StarTimeseries(time=l1, mag=l2, error=l3)


@given(
    lists(text(alphabet=string.ascii_letters, min_size=1), min_size=1),
    lists(floats(), min_size=1),
    lists(floats(), min_size=1),
)
def test_bad_conversion(ls, lf1, lf2):
    assume(len(ls) == len(lf1))
    assume(len(ls) == len(lf2))
    with pytest.raises(ValueError):
        StarTimeseries(time=ls, mag=lf1, error=lf2)


@given(
    three_lists(floats(allow_infinity=False), min_size=1),
)
def test_conversion(data):
    lf, li, ls = data
    sts = StarTimeseries(time=lf, mag=li, error=ls)
    assert pd.is_numeric_dtype(sts.error)
    assert pd.is_numeric_dtype(sts.mag)
    assert isinstance(sts.time, pd.DatetimeIndex)


@given(three_lists(text(alphabet=string.digits), min_size=1))
def test_conversion_text(data):
    lf, li, ls = data
    sts = StarTimeseries(time=lf, mag=li, error=ls)
    assert pd.is_numeric_dtype(sts.error)
    assert pd.is_numeric_dtype(sts.mag)
    assert isinstance(sts.time, pd.DatetimeIndex)


@given(three_lists(integers(), min_size=1))
def test_conversion_integers(data):
    lf, li, ls = data
    sts = StarTimeseries(time=lf, mag=li, error=ls)
    assert pd.is_numeric_dtype(sts.error)
    assert pd.is_numeric_dtype(sts.mag)
    assert isinstance(sts.time, pd.DatetimeIndex)
