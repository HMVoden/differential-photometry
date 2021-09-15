import pandas as pd
import xarray as xr
from typing import Union


def _pandas_to_xarray(frame: pd.DataFrame) -> xr.Dataset:
    if isinstance(frame, (xr.Dataset)):
        return frame
    return frame.to_xarray()


def _xarray_to_pandas(frame: xr.Dataset) -> pd.DataFrame:
    if isinstance(frame, (pd.DataFrame, pd.Series)):
        return frame
    return frame.to_pandas()


def convert_frame(
    frame: Union[pd.DataFrame, pd.Series, xr.DataArray, xr.Dataset], to: str
) -> Union[pd.DataFrame, pd.Series, xr.DataArray, xr.Dataset, None]:
    if to == "pandas":
        return _xarray_to_pandas(frame)
    if to == "xarray":
        return _pandas_to_xarray(frame)
    raise ValueError("Invalid frame type, only supported frames are: pandas, xarray")
