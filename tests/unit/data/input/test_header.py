import pytest
from hypothesis import assume, given
from hypothesis.strategies import lists, text
from shutterbug.data.input.header import Header


@given(lists(text(min_size=1)), lists(text(min_size=1)))
def test_header_class(l1, l2):
    header1 = Header(headers=l1)
    header2 = Header(headers=l2)
    s1 = set(l1)
    s2 = set(l2)
    if s1.intersection(s2) == s1 and s2.intersection(s1) == s2:
        assert header1 == header2
    else:
        assert header1 != header2


@given(lists(text(min_size=1)), lists(text(min_size=1)))
def test_header_different_lengths(l1, l2):
    assume(len(l1) != len(l2))
    h1 = Header(headers=l1)
    h2 = Header(headers=l2)
    assert h1 != h2
