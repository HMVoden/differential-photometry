from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from arch.unitroot import ADF, DFGLS, KPSS, ZivotAndrews
from scipy.stats import chisquare
from shutterbug.photometry.detect.detect import DetectBase


@dataclass
class StationarityTestStrategy(ABC):
    test_method: str

    @abstractmethod
    def test(self, data: npt.NDArray) -> float:
        pass


@dataclass
class VariationDetector(DetectBase):
    p_value: float
    clip_data: bool
    null: str
    tester: StationarityTestStrategy

    def detect(self, data: npt.NDArray) -> Tuple[bool, float, str]:
        p_value = self.p_value
        null = self.null
        tester = self.tester
        test_result = tester.test(data)
        varying = False

        if null == "accept":
            varying = test_result >= p_value
        else:
            varying = test_result <= p_value
        return varying, test_result, tester.test_method


@dataclass
class ReducedChiSquare(StationarityTestStrategy):
    expected: Optional[npt.NDArray] = None
    parameters_estimated: Optional[int] = None

    def test(self, data: npt.NDArray) -> float:
        data = np.asanyarray(data)
        p_est = self.parameters_estimated
        expected = self.expected
        if p_est is None:
            p_est = 1
        if expected is None:
            p_est += 1
            expected = np.median(data)
        variance = np.var(data, ddof=1)
        dof = data.shape[0] - p_est - 1
        chi = np.sum(((data - expected) ** 2 / variance)) / dof
        return chi


@dataclass
class ChiSquare(StationarityTestStrategy):
    """Performs the chi squared test on the provided data.

    Further reading: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chisquare.html#scipy.stats.chisquare

    Configured in photometry.toml"""

    ddof: Optional[int]
    expected: Optional[str]

    def test(self, data):
        ddof = self.ddof
        expected = self.expected
        if expected == "mean":
            expected = np.average(data)
        elif expected == "median":
            expected = np.median(data)
        elif expected == "weighted_mean":
            expected = np.average(data, weights=(1 / error ** 2))

        result = chisquare(f_obs=data, f_exp=expected, ddof=ddof)
        return result[1]  # p-value


@dataclass
class AugmentedDFullerTest(StationarityTestStrategy):
    max_lags: int
    trend: str
    method: str
    """Performs the augmented Dickey-Fuller test on the data.
    The null hypothesis of this test is that the timeseries inputted is NOT stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.ADF.html

    This is configured in photometry.toml

    Parameters
    ----------
    data : list-like
        Timeseries to test stationarity on

    Returns
    -------
    float
        the p-value of the test statistic
    """

    def test(self, data):
        max_lags = self.max_lags
        trend = self.trend
        method = self.method
        result = ADF(data, max_lags=max_lags, trend=trend, method=method)
        return result.pvalue


@dataclass
class KPSSTest(StationarityTestStrategy):
    trend: str
    lags: int
    """Performs the Kwiatkowski–Phillips–Schmidt–Shin test of stationarity on the inputted data.
    The null hypothesis of this test is that the timeseries inputted is stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.DFGLS.html#arch.unitroot.DFGLS

    This is configured in photometry.toml

    """

    def test(self, data):
        lags = self.lags
        trend = self.trend
        result = KPSS(data, trend=trend, lags=lags)
        return result.pvalue


@dataclass
class ZivotAndrewsTest(StationarityTestStrategy):
    trend: str
    trim: float
    method: str
    max_lags: int
    """Performs the non-parametric Zivot-Andrews test of timeseries
    stationarity on the inputted data.
    The null hypothesis of this test is that the timeseries inputted is stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.ZivotAndrews.html

    This is configured in photometry.toml

    """

    def test(self, data):
        max_lags = self.max_lags
        trend = self.trend
        method = self.method
        trim = self.trim
        result = ZivotAndrews(
            data, trend=trend, trim=trim, method=method, max_lags=max_lags
        )
        return result.pvalue


@dataclass
class ADFGLSTest(StationarityTestStrategy):
    """Performs the GLS-version of the augmented Dickey-Fuller test on the data.
    The null hypothesis of this test is that the timeseries inputted is
    NOT stationary.

    Further reading:
    https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.DFGLS.html#arch.unitroot.DFGLS

    This is configured in photometry.toml

    """

    trend: str
    max_lags: int
    method: str

    def test(self, data):
        max_lags = self.max_lags
        trend = self.trend
        method = self.method
        result = DFGLS(data, trend=trend, method=method, max_lags=max_lags)
        return result.pvalue


def normalize(data: np.ndarray) -> np.ndarray:
    """Takes a dataset and normalizes it to between 0-1

    Parameters
    ----------
    data : np.ndarray
        Data to normalize

    Returns
    -------
    np.ndarray
        Normalized data
    """
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data - data_min) / (data_max - data_min)
    return normalized


def normalize_to_std(df: pd.DataFrame) -> pd.DataFrame:
    """Finds the mean of every numerical column in the dataframe, its standard deviation
    then converts it to a z-score. For use in machine learning

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing numerical values to normalize (in a Gaussian sense)

    Returns
    -------
    pd.DataFrame
        Dataframe that has been normalized
    """
    df_mean = df.mean()
    df_std = df.std()
    df_norm = (df - df_mean) / df_std
    return df_norm


def normalize_to_median(data: np.ndarray) -> np.ndarray:
    """Takes a dataset and brings the median to 1

    Parameters
    ----------
    data : np.ndarray
        Dataset to normalize

    Returns
    -------
    np.ndarray
        Normalized dataset
    """
    median = np.median(data)
    return data / median
