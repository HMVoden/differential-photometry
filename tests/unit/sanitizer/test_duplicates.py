import numpy as np
from hypothesis import given
from hypothesis.strategies import composite, floats, lists, text
from shutterbug.data_sanitizer.clean.duplicates import find_duplicates


@composite
def equal_length_lists_float_text(draw):
    nums = draw(lists(floats(allow_nan=True, allow_infinity=False), min_size=1))
    txt = draw(lists(text(), max_size=len(nums), min_size=len(nums)))
    return nums, txt


@given(equal_length_lists_float_text())
def test_find_duplicates(data):
    numerical, textual = data
    hashmap = {}
    for tup in zip(numerical, textual):
        if tup in hashmap:
            hashmap[tup] += 1
        else:
            hashmap[tup] = 1
    values = np.asarray(list(hashmap.values())).flatten() - 1
    number_duplicates = np.count_nonzero(values)
    duplicate_indices = find_duplicates(numerical, textual)
    assert number_duplicates == len(duplicate_indices)
