import string
from typing import Dict, List

import hypothesis.strategies as st
import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis.extra.pandas import column, data_frames
from hypothesis.strategies import composite
from shutterbug.sanitizer.pandas_sanitizer import _clean_names


@composite
def dirty_panda_frames(draw):
    names = draw(st.lists(st.text(min_size=1), min_size=1))
    data = draw(st.lists(st.floats(), min_size=len(names), max_size=len(names)))
    ind = pd.Index(data)
    data_dict = dict(zip(names, data))
    return pd.DataFrame(data_dict, index=ind)


@given(dirty_panda_frames())
def test_clean_pandas_names(dirty_frame):
    not_allowed = string.punctuation
    clean_named_frame = _clean_names(dirty_frame)
    for name in clean_named_frame.columns:
        assert all([True if x not in not_allowed else False for x in name])
