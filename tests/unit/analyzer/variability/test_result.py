import pytest
from shutterbug.analyzer.variability.result import TestResult


def test_proper():
    result = TestResult(pvalue=0.05, null="accept")
    assert result.pvalue == 0.05
    assert result.null == "accept"

+
def test_bad_pvalue():
    with pytest.raises(ValueError):
        result = TestResult(pvalue="0.05", null="reject")


def test_bad_null():
    with pytest.raises(ValueError):
        result = TestResult(pvalue=0.05, null="potato")


def test_bad_both():
    with pytest.raises(ValueError):
        result = TestResult(pvalue="0.05", null=7)
