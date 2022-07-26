from typing import List

import numpy as np
import pandas as pd

from shutterbug.data import Star


def average_differential(
    target: Star,
    reference: List[Star],
) -> Star:

    """Given a target star and a list of reference stars, calculates the average
    differential magnitude and error for target

    :param target: Target star to calculate on
    :param reference: Reference stars to use for calculate
    :returns: Star updated with average differential magnitude and error

    """
    if len(reference) < 1:
        raise ValueError(
            "Need at least one reference star for differential photometry, exiting"
        )
    target_mag = target.timeseries.magnitude
    target_error = target.timeseries.error
    reference_mag = reference[0].timeseries.magnitude
    reference_error = reference[0].timeseries.error
    # Unpack reference list
    for ref in reference[1:]:
        reference_mag = pd.concat([ref.timeseries.magnitude, reference_mag])
        reference_error = pd.concat([ref.timeseries.error, reference_error])
    ade = _average_error(target=target_error, reference=reference_error)
    adm = _average_difference(target=target_mag, reference=reference_mag)
    target.timeseries.differential_magnitude = adm
    target.timeseries.differential_error = ade
    return target


def _average_error(
    target: pd.Series,
    reference: pd.Series,
) -> pd.Series:

    """Calculates the average differential error of given star's timeseries

    :param target: Target star timeseries
    :param reference: Reference stars timeseries
    :returns: New timeseries containing the averaged differential error

    """
    # Number of reference stars
    N = reference.groupby("time").count()[0]
    # Propagation of average
    new = np.sqrt((reference**2 + target**2).groupby("time").sum()) / N
    return new


def _average_difference(
    target: pd.Series,
    reference: pd.Series,
) -> pd.Series:

    """Calculates the average differential magnitude of a given star's timeseries
    compared with a set of reference star's timeseries

    :param target: Target star timeseries
    :param reference: Reference stars timeseries
    :returns: New timeseries containing the averaged differential magnitude

    """
    new = reference.sub(target).groupby("time").mean()
    return new
