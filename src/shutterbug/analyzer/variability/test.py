from dataclasses import dataclass
from typing import Literal, Optional, Sequence

from arch.unitroot import ADF
from shutterbug.analyzer.variability.result import TestResult
from shutterbug.analyzer.variability.test_interface import \
    VariabilityDataTestInterface


@dataclass
class AugmentedDFTest(VariabilityDataTestInterface):
    trend: str
    method: str
    null = "accept"
    max_lags: Optional[int] = None

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

    def test(self, data: Sequence[float]) -> TestResult:
        max_lags = self.max_lags
        trend = self.trend
        method = self.method
        result = ADF(y=data, max_lags=max_lags, trend=trend, method=method)
        test_result = TestResult(null=self.null, pvalue=result.pvalue)
        return test_result
