import logging

import pandas as pd
from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    adm = star.timeseries.differential_magnitude
    star.timeseries.add_feature(
        adm.agg(**{test.internal_name: pd.NamedAgg(aggfunc=test)})
    )
    return star


def is_variable(star: Star, threshold: float, test_name: str) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    feature = star.timeseries.features[test_name]
    if (feature >= threshold).any:
        star.variable = True
    else:
        star.variable = False
    return star
