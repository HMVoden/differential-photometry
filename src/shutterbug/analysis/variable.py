from typing import Dict

from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(data: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    adm = data.timeseries.differential_magnitude
    data.timeseries.add_feature(test.name, test(adm))
    return data


def is_variable(data: Star, threshold: float) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    features = data.timeseries.features
    variable_tests = []
    for result in features.values():
        variable_tests.append(result > threshold)
    data.variable = any(variable_tests)
    return data
