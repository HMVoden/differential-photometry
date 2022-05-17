import logging
from typing import List

import pandas as pd
from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    data = star.timeseries.differential_magnitude
    results = data.groupby(data.index.date).agg(**{test.name: test})
    for date, value in results.itertuples(index=True):
        star.timeseries.add_feature(date=str(date), name=test.name, value=value)
    return star


def is_variable(star: Star, tests: List[FeatureBase]) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    pass
