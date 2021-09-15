from typing import Union

from pandas.core.frame import DataFrame
from shutterbug.file_loader.converter import (
    _pandas_to_xarray,
    _xarray_to_pandas,
    convert_frame,
)
import pandas as pd
import xarray as xr
import pytest


@pytest.fixture(params=[pd.DataFrame(), pd.Series(), xr.Dataset()])
def dataframes(request):
    return request.param


def test_conversion_to_xarray():
    frame = pd.DataFrame()
    converted_frame = _pandas_to_xarray(frame)
    assert isinstance(converted_frame, xr.Dataset)


def test_conversion_to_pandas():
    frame = xr.Dataset()
    converted_frame = _xarray_to_pandas(frame)
    assert isinstance(converted_frame, pd.Series)


def test_convert_frame_pandas(dataframes):
    print(dataframes)
    converted_frame = convert_frame(dataframes, "pandas")
    assert isinstance(converted_frame, (pd.Series, pd.DataFrame))


def test_convert_frame_xarray(dataframes):
    assert isinstance(convert_frame(dataframes, "xarray"), (xr.DataArray, xr.Dataset))


def test_convert_frame_other(dataframes):
    with pytest.raises(ValueError):
        convert_frame(dataframes, "potato")
