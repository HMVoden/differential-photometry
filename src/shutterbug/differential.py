from typing import Optional
import pandas as pd
import numpy as np


def average_differential(
    target: pd.DataFrame,
    reference: pd.DataFrame,
    data_column: str = "mag",
    error_column: Optional[str] = None,
) -> pd.DataFrame:

    """Calculates the average differential magnitude of each time point for a target star, given reference stars.

    :param target: Star with data column to find differential magnitude of
    :param reference: Reference stars with data column
    :param data_column: Data column name
    :param error_column: Error column name, optional
    :returns: Dataframe of the average differential magnitude of the star with error if given

    """
    average_differential_magnitude = _average_difference(
        target=target[data_column], reference=reference[data_column]
    )
    average_differential_magnitude = average_differential_magnitude.dropna(
        axis=0, how="any"
    )
    average_differential_magnitude.rename("adm")  # type: ignore
    if error_column is not None:
        average_differential_error = _average_error(
            target=target[error_column], reference=reference[error_column]
        )
        average_differential_error = average_differential_error.dropna(
            axis=0, how="any"
        )
        average_differential_error = average_differential_error.rename(  # type: ignore
            "ade"
        )
        return pd.concat(
            {"adm": average_differential_magnitude, "ade": average_differential_error},  # type: ignore
        )
    else:
        return average_differential_magnitude  # type: ignore


def _average_error(
    target: pd.Series,
    reference: pd.Series,
) -> pd.Series:
    """Calculates the average error for the target error column

    :param target: Error pandas series of target star
    :param reference: Error pandas series of reference stars
    :returns: Average differential error timeseries

    """

    N = len(reference.groupby("name")) + 1
    new = (
        np.sqrt((reference ** 2 + target.droplevel("name") ** 2).groupby("time").sum())
        / N
    )
    return new


def _average_difference(
    target: pd.Series,
    reference: pd.Series,
) -> pd.Series:

    """Calculates the average difference between target and reference stars

    :param target: Magnitude pandas series of target star
    :param reference: Magnitude pandas series of reference stars
    :returns: Average differential magnitude timeseries

    """
    new = reference.rsub(target.droplevel("name")).groupby("time").mean()
    return new
