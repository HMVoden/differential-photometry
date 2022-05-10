import logging
from typing import List

from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    data = star.timeseries.differential_magnitude
    results = data.groupby(data.index.date).agg(test)
    print(results)


def is_variable(star: Star, tests: List[FeatureBase]) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    pass
