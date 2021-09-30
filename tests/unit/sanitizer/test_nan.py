import numpy as np
from hypothesis import given
from hypothesis.strategies import floats, lists
from shutterbug.data_sanitizer.clean.nan import clean_nan, find_nan


@given(lists(floats(allow_infinity=False, allow_nan=True)))
def test_find_nan(numerical_data):
    numerical_data = np.asarray(numerical_data).flatten()
    num_nans = np.count_nonzero(np.isnan(numerical_data))
    nan_indices = find_nan(numerical_data)
    assert len(nan_indices) == num_nans
    cleaned = np.delete(numerical_data, nan_indices)
    assert np.count_nonzero(np.isnan(cleaned)) == 0


@given(lists(floats(allow_infinity=False, allow_nan=True)))
def test_clean_nan(numerical_data):
    numerical_data = np.asarray(numerical_data).flatten()
    cleaned = clean_nan(numerical_data)
    assert np.count_nonzero(np.isnan(cleaned)) == 0
