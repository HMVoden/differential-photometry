from typing import List, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from scipy.stats import mode
from shutterbug.sanitizer.duplicates import find_duplicates
from shutterbug.sanitizer.names import clean_names
from shutterbug.sanitizer.nan import find_nan
from shutterbug.sanitizer.sanitizer_interface import SanitizerInterface


class XarraySanitizer(SanitizerInterface):
    def sanitize(
        self,
        frame: xr.Dataset,
        primary_variables: List[str],
        numeric_variables: Optional[List[str]] = None,
        discard_variables: Optional[List[str]] = None,
        keep_variables: Optional[List[str]] = None,
        keep_duplicates: Optional[str] = "first",
    ) -> xr.Dataset:
        return (
            frame.pipe(self._clean_names)
            .pipe(self._discard_variables, discard_variables)
            .pipe(self._keep_variables, keep_variables)
            .pipe(self._coerce_into_numeric, numeric_variables)
            .pipe(self._drop_duplicates, primary_variables, keep_duplicates)
            .pipe(self._drop_nan)
            .pipe(self._remove_abnormal_count_variables, primary_variables)
        )

    def _clean_names(self, frame: xr.Dataset) -> xr.Dataset:
        cleaned = clean_names(list(frame.keys()))
        rename_dict = dict(zip(list(frame.keys()), cleaned))
        frame = frame.rename(rename_dict)
        return frame

    def _coerce_into_numeric(
        self, frame: xr.Dataset, numeric_variables: Optional[List[str]] = None
    ) -> xr.Dataset:
        if numeric_variables is not None:
            numeric_variables = clean_names(numeric_variables)
            for var in numeric_variables:
                frame[var] = pd.to_numeric(frame[var], errors="coerce")
        return frame

    def _discard_variables(
        self, frame: xr.Dataset, discard_variables: Optional[List[str]] = None
    ) -> xr.Dataset:
        if discard_variables is not None:
            discard_variables = clean_names(discard_variables)
            frame = frame.drop_vars(discard_variables)
        return frame

    def _keep_variables(
        self, frame: xr.Dataset, keep_variables: Optional[List[str]] = None
    ) -> xr.Dataset:
        if keep_variables is not None:
            variables = list(frame.keys())
            discard = [x if x not in keep_variables else "" for x in variables]
            frame = frame.drop_vars(discard)
        return frame

    def _drop_duplicates(
        self,
        frame: xr.Dataset,
        primary_variables: Optional[List[str]],
        keep_duplicates: Optional[str] = "first",
    ) -> xr.Dataset:
        primary_variables = clean_names(primary_variables)
        data = []
        for var in primary_variables:
            data.append(frame[var].data)
        duplicate_indices = find_duplicates(*data)
        to_drop = []
        for indices in duplicate_indices:
            if keep_duplicates == "first":
                to_drop.extend(indices[1:])
            elif keep_duplicates == "last":
                to_drop.extend(indices[:-1])
            else:
                to_drop.extend(indices)
        return frame.drop_isel(to_drop)

    def _remove_abnormal_count_variables(
        self, frame: xr.Dataset, primary_variables: List[str]
    ) -> xr.Dataset:
        primary_variables = clean_names(primary_variables)
        for var in primary_variables:
            deviated = self._find_indices_deviated_from_mode(frame[var])
            frame = frame.drop_isel(deviated)
        return frame

    def _find_indices_deviated_from_mode(
        self, dataarray: xr.DataArray, return_mode: Optional[bool] = False
    ) -> Union[xr.DataArray, Tuple[xr.DataArray, npt.NDArray[np.int_]]]:
        counts = dataarray.count()
        # data for numpy array, axis=None to make sure it's flat
        array_mode, _ = mode(counts.data, axis=None)
        deviated = counts[counts != array_mode].indexes
        if return_mode is True:
            return (deviated, array_mode)
        else:
            return deviated

    def _drop_nan(self, frame: xr.Dataset) -> xr.Dataset:
        for name in frame.indexes.keys():
            frame.dropna(dim=name, how="any")
        return frame
