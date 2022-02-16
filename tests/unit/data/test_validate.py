from shutterbug.data.validate import _is_same_length, _has_data, _empty_rows

from hypothesis import given
from hypothesis.strategies import lists, floats
import pytest
import numpy as np


@given(lists(lists(floats())))
def test_is_same_length(lists):
    if len(lists) == 0:
        assert _is_same_length(*lists)
    else:
        length = len(lists[0])
        equal = True
        for list in lists[1:]:
            if len(list) != length:
                equal = False
                break
        assert _is_same_length(*lists) == equal


@given(
    lists(
        lists(floats(allow_infinity=False, allow_subnormal=False), min_size=1),
        min_size=1,
    )
)
def test_empty_rows(lists):
    same_length = _is_same_length(*lists)
    if not same_length:
        with pytest.raises(ValueError):
            _empty_rows(*lists)
    else:
        rows = np.asarray(lists, dtype="float32")
        indexes = []
        for idx, row in enumerate(rows):
            if np.isnan(row).all():
                indexes.append(idx)
        test_results = _empty_rows(*lists)
        assert set(test_results) == set(indexes)
        assert len(test_results) == len(indexes)


@given(lists(floats(allow_infinity=False)))
def test_has_data(data):
    if np.isnan(data).all():
        assert _has_data(data) == False
    else:
        assert _has_data(data) == True
