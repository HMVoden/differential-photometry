import logging
from typing import List, Optional

import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from shutterbug.sanitizer.names import clean_name, clean_names
from shutterbug.sanitizer.sanitizer_interface import SanitizerInterface


class PandasSanitizer(SanitizerInterface):
    def sanitize(
        self,
        frame: pd.DataFrame,
        primary_variables: List[str],
        numeric_variables: Optional[List[str]] = None,
        discard_variables: Optional[List[str]] = None,
        keep_variables: Optional[List[str]] = None,
        keep_duplicates: Optional[str] = "first",
    ) -> pd.DataFrame:
        frame = (
            frame.pipe(self._clean_names)
            .pipe(self._discard_variables, discard_variables)
            .pipe(self._keep_variables, keep_variables)
            .pipe(self._coerce_into_numeric, numeric_variables)
            .pipe(self._drop_duplicates, primary_variables, keep_duplicates)
            .pipe(self._drop_nan)
            .pipe(self._remove_abnormal_count_variables, primary_variables)
        )
        frame = frame.rename_axis("index")
        return frame

    def _clean_names(self, frame: pd.DataFrame) -> pd.DataFrame:
        logging.info("Cleaning header names")
        return frame.rename(clean_name, axis="columns", errors="raise")

    def _coerce_into_numeric(
        self, frame: pd.DataFrame, numeric_variables: Optional[List[str]] = None
    ) -> pd.DataFrame:
        logging.info(f"Coercing into numeric types: {', '.join(numeric_variables)}")
        if numeric_variables is not None:
            for col in numeric_variables:
                frame[col] = pd.to_numeric(frame[col], errors="coerce")
            frame = frame.dropna(how="all")
        return frame

    def _discard_variables(
        self, frame: pd.DataFrame, discard_variables: Optional[List[str]] = None
    ) -> pd.DataFrame:
        if discard_variables is not None:
            logging.info("Dropping variables: {', '.join(discard_variables)}")
            frame = frame.drop(columns=discard_variables)
        return frame

    def _keep_variables(
        self, frame: pd.DataFrame, keep_variables: Optional[List[str]] = None
    ) -> pd.DataFrame:
        if keep_variables is not None:
            logging.info(f"Keeping only variables: {', '.join(keep_variables)}")
            variables = list(frame.columns)
            discard = [x for x in variables if x not in keep_variables]
            # discard = [x if x not in keep_variables else pass for x in variables]
            frame = frame.drop(columns=discard)
        return frame

    def _remove_abnormal_count_variables(
        self, frame: pd.DataFrame, primary_variables: List[str]
    ) -> pd.DataFrame:
        logging.info(
            f"Removing abnormal counts from variables: {', '.join(primary_variables)}"
        )
        for var in primary_variables:
            deviated = self._find_indices_deviated_from_mode(frame[var])
            logging.info(
                f"Removing from variable '{var}': {' '.join(deviated.index.array.astype(str))}"
            )
            deviated = deviated.index.values
            frame = frame[~frame[var].isin(deviated)]
        return frame

    def _find_indices_deviated_from_mode(
        self, series: pd.Series, return_mode: Optional[bool] = False
    ) -> pd.Series:
        counts = series.value_counts()
        series_mode = counts.mode().values[0]
        logging.info(f"Found mode of variable '{series.name}' to be {series_mode}")
        deviated = counts[counts != series_mode]
        logging.info(f"Found {len(deviated)} bad rows")
        if return_mode is True:
            return (deviated, mode)
        else:
            return deviated

    def _drop_duplicates(
        self,
        frame: pd.DataFrame,
        primary_variables: Optional[List[str]],
        keep_duplicates: Optional[str] = "first",
    ) -> pd.DataFrame:
        logging.debug(
            f"Dropping duplicate entries using headers {', '.join(primary_variables)} as keys"
        )
        frame = frame.drop_duplicates(subset=primary_variables, keep=keep_duplicates)
        return frame

    def _drop_nan(self, frame: pd.DataFrame) -> pd.DataFrame:
        return frame.dropna(axis="index", how="all")
