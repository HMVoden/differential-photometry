import logging

from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    pass


def is_variable(star: Star, threshold: float, test_name: str) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    pass
