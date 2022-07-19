from __future__ import annotations

import logging
import sys
from datetime import date
from typing import Dict, List, Union

import numpy as np
import numpy.typing as npt
import pandas as pd
from attr import define, field
from shutterbug.data.header import KnownHeader
from shutterbug.data.validate import _empty_rows, _has_data, _is_same_length


def asfloat(value: List[str]) -> npt.NDArray[np.float32]:
    return pd.to_numeric(value, errors="coerce", downcast="float")  # type: ignore


def asdatetime(value) -> pd.DatetimeIndex:
    try:
        # Try julian date
        fl = pd.to_numeric(value, errors="coerce")
        datetimes = pd.to_datetime(
            fl, errors="coerce", origin="julian", unit="D", utc=True
        )
        if all(pd.isna(datetimes)):
            raise ValueError
    except (ValueError, NameError):
        # Try guessing
        datetimes = pd.to_datetime(value, errors="coerce", utc=True)
    datetimes = datetimes.round("1us")
    return pd.DatetimeIndex(datetimes, name="time", yearfirst=True)


@define(slots=True)
class StarTimeseries:
    """Timeseries information for a star"""

    data: pd.DataFrame = field()
    _features: Dict[date, Dict[str, float]] = field(init=False, default={})

    def __attrs_post_init__(self):
        self._features = {}

    @property
    def time(self) -> pd.DatetimeIndex:
        return self.data.index  # type: ignore

    @property
    def magnitude(self) -> pd.Series:
        return self.data["magnitude"]

    @magnitude.setter
    def magnitude(self, data: pd.Series) -> None:
        self.data["magnitude"] = data

    @property
    def error(self) -> pd.Series:
        return self.data["error"]

    @error.setter
    def error(self, data: pd.Series) -> None:
        self.data["error"] = data

    @property
    def differential_magnitude(self) -> pd.Series:
        if "adm" in self.data.columns:
            return self.data["adm"]
        else:
            return pd.Series(dtype="float32")

    @differential_magnitude.setter
    def differential_magnitude(self, data: pd.Series) -> None:
        self.data["adm"] = data

    @property
    def differential_error(self) -> pd.Series:
        if "ade" in self.data.columns:
            return self.data["ade"]
        else:
            return pd.Series(dtype="float32")

    @differential_error.setter
    def differential_error(self, data: pd.Series) -> None:
        self.data["ade"] = data

    def drop_rows(self, rows: List[int]) -> None:
        row_indices = self.data.index.to_numpy()[rows]
        self.data = self.data.drop(index=row_indices)  # type: ignore

    def __eq__(self, other: StarTimeseries):
        if other.__class__ is not self.__class__:
            return NotImplemented

        return (
            other.magnitude.equals(self.magnitude)
            and other.error.equals(self.error)
            and other.differential_error.equals(self.differential_error)
            and other.differential_magnitude.equals(self.differential_magnitude)
            and other.features == self.features
        )

    @property
    def features(self) -> Dict[date, Dict[str, float]]:
        return self._features.copy()

    def add_feature(self, dt: date, name: str, value: float) -> None:
        features = self._features
        if dt in features:
            features[dt][name] = value
        else:
            features[dt] = {name: value}
        self._features = features

    @property
    def nbytes(self) -> int:
        """Number of bytes the timeseries consumes in memory"""
        return self.data.nbytes

    @classmethod
    def from_rows(
        cls, rows: List[List[str]], row_headers: KnownHeader
    ) -> StarTimeseries:
        logging.debug(f"Building timeseries, number of rows: {len(rows)}")
        getter = row_headers.timeseries_getters
        timeseries = list(map(getter, rows))
        # so we can get each specific column without fuss
        np_data = np.asarray(timeseries)
        df = pd.DataFrame(
            data={"magnitude": asfloat(np_data[:, 1]), "error": asfloat(np_data[:, 2])},
            index=asdatetime(np_data[:, 0]),
        )

        ts = cls(data=df)  # type: ignore
        ts = validate_timeseries(ts)
        logging.debug("Finished building timeseries")
        return ts


@define(slots=True)
class Star:
    """Dataclass describing a star's information"""

    name: str = field()
    # First to float and then to int to prevent odd reading errors
    x: int = field(converter=[float, int])
    y: int = field(converter=[float, int])
    timeseries: StarTimeseries = field()
    variable: bool = field(default=False)

    @property
    def nbytes(self) -> int:
        """Number of bytes the star consumes in memory"""
        return (
            sys.getsizeof(self.name)
            + sys.getsizeof(self.x)
            + sys.getsizeof(self.y)
            + self.timeseries.nbytes
        )

    @classmethod
    def from_rows(
        cls, rows: List[List[str]], row_headers: KnownHeader
    ) -> Union[Star, None]:
        name, x, y = row_headers.star_getters(rows[0])
        logging.info(f"Building star object {name}, x: {x}, y: {y}")
        try:
            timeseries = StarTimeseries.from_rows(rows, row_headers)
        except ValueError as e:
            logging.error(f"Unable to create timeseries, received error: {e}")
            return None
        return cls(name=name, x=x, y=y, timeseries=timeseries)

    def __eq__(self, other: Star):
        if other.__class__ is not self.__class__:
            return NotImplemented

        return (
            other.x == self.x
            and other.y == self.y
            and other.variable == self.variable
            and other.timeseries == self.timeseries
        )

    def to_dataframe(self) -> pd.DataFrame:
        df = self.timeseries.data
        df["x"] = self.x
        df["y"] = self.y
        df["name"] = self.name
        df["variable"] = self.variable
        return df


def validate_timeseries(ts: StarTimeseries) -> StarTimeseries:
    mag = ts.magnitude.to_numpy()
    error = ts.error.to_numpy()
    ts.drop_rows(_empty_rows(mag, error))
    try:
        assert _is_same_length(mag, error)
    except AssertionError:
        raise ValueError("Magnitude and error are not the same length")
    try:
        assert _has_data(mag)
        assert _has_data(error)
    except AssertionError:
        raise ValueError("Either magnitude or error has no values")
    return ts
