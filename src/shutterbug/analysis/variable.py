from typing import List

from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase, by_day: bool = True) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    data = star.timeseries.differential_magnitude
    if by_day:
        results = data.groupby(data.index.date).agg(**{test.name: test})
        for date, value in results.itertuples(index=True):
            star.timeseries.add_feature(dt=date, name=test.name, value=value)

    else:
        results = data.agg(**{test.name: test})
        for date in data.index.date:
            star.timeseries.add_feature(
                dt=date, name=test.name, value=results.to_numpy()[0]
            )

    return star


def test_variability(star: Star, tests: List[FeatureBase]) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    for test in tests:
        for date in star.timeseries.features.keys():
            if star.timeseries.features[date][test.name] >= test.threshhold:
                star.variable = True
                return star
    return star
