import string

from hypothesis import given
from hypothesis.strategies import lists, text
from shutterbug.data_sanitizer.clean.names import clean_names


@given(lists(text()))
def test_clean_names(names):
    not_allowed = set(string.punctuation)
    cleaned = clean_names(names)
    for name in cleaned:
        assert all([True for x in name if x not in not_allowed])
