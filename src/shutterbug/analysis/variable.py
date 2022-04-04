import logging

from shutterbug.analysis.feature import FeatureBase
from shutterbug.data import Star


def run_test(star: Star, test: FeatureBase) -> Star:
    """Runs given statistical feature test on star's differential magnitude data
    and adds result to timeseries"""
    adm = star.timeseries.differential_magnitude
    star.timeseries.add_feature(test.name, test(adm))
    return star


def is_variable(star: Star, threshold: float) -> Star:
    """Determines if a star is variable by iterating through all timeseries
    features and flagging if any are True"""
    features = star.timeseries.features
    for result in features.values():
        if result > threshold:
            star.variable = True
            logging.debug(f"Star {star.name} found as variable")
            return star
    return star
