import pytest
from hypothesis import given
from hypothesis.strategies import lists, text
from shutterbug.data.header import Header, KnownHeader
import string


@given(lists(text(min_size=1)), lists(text(min_size=1)))
def test_header_class(l1, l2):
    header1 = Header(headers=l1)
    header2 = Header(headers=l2)
    s1 = set(l1)
    s2 = set(l2)
    if s1.issuperset(s2):
        assert header1 == header2
    else:
        assert header1 != header2


@given(lists(text(alphabet=string.ascii_letters, min_size=1), min_size=3, unique=True))
def test_known_headers(data):
    kh = KnownHeader(
        header_origin="Test",
        headers=data,
        timeseries_names=[data[1], data[2]],
        star_data=[data[0]],
        star_name=data[0],
    )
    timeseries = [*kh.timeseries_getters(data)]
    star_data = [kh.star_getters(data)]
    name_index = kh.name_index

    assert name_index == 0
    assert star_data == [data[0]]
    assert timeseries == [data[1], data[2]]
