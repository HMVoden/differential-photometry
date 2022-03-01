from shutterbug.data.star import Star
from shutterbug.analysis.feature import FeatureBase
from typing import Dict


def run_test(data: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    adm_ade = data.timeseries.averaged_differential_magnitude
    data.timeseries.add_feature(test.name, test(adm_ade))
    return data


def is_variable(data: Star, thresholds: Dict[str, float]) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    features = data.timeseries.features
    variable_tests = []
    for name, result in features.items():
        if name in thresholds:
            variable_tests.append(result > thresholds[name])
    data.variable = any(variable_tests)
    return data
