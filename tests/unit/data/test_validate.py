import numpy as np
import pytest
from hypothesis import given
from hypothesis.strategies import floats, lists
from shutterbug.data.validate import _empty_rows, _has_data, _is_same_length


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
def test_empty_rows(columns):
    same_length = _is_same_length(*columns)
    if not same_length:
        with pytest.raises(ValueError):
            _empty_rows(*columns)
    else:
        rows = np.asarray(columns, dtype="float32").T
        indexes = []
        for idx, row in enumerate(rows):
            if np.isnan(row).all():
                indexes.append(idx)
        test_results = _empty_rows(*columns)
        assert set(test_results) == set(indexes)
        assert len(test_results) == len(indexes)


@given(lists(floats(allow_infinity=False)))
def test_has_data(data):
    if np.isnan(data).all():
        assert _has_data(data) == False
    else:
        assert _has_data(data) == True
