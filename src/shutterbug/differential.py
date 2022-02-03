from typing import Optional
import pandas as pd
import numpy as np


def average_differential(
    target: pd.DataFrame,
    reference: pd.DataFrame,
    data_column: str = "mag",
    error_column: Optional[str] = None,
) -> pd.DataFrame:
    average_differential_magnitude = _average_difference(
        target=target[data_column], reference=reference[data_column]
    )
    average_differential_magnitude = average_differential_magnitude.dropna(
        axis=0, how="any"
    )
    average_differential_magnitude.rename({data_column: "adm"})  # type: ignore
    if error_column is not None:
        average_differential_error = _average_error(
            target=target[error_column], reference=reference[error_column]
        )
        average_differential_error = average_differential_error.dropna(
            axis=0, how="any"
        )
        average_differential_error = average_differential_error.rename(  # type: ignore
            {error_column: "ade"}
        )
        return pd.concat(
            {"adm": average_differential_magnitude, "ade": average_differential_error},  # type: ignore
            axis=1,
        )
    else:
        return average_differential_magnitude  # type: ignore


def _average_error(
    target: pd.Series,
    reference: pd.Series,
) -> pd.DataFrame:
    N = len(reference.groupby("name")) + 1
    new = np.sqrt((reference ** 2 + target ** 2).groupby("name").sum()) / N
    return new


def _average_difference(
    target: pd.Series,
    reference: pd.Series,
) -> pd.DataFrame:
    print(target - reference)
    new = (target - reference).groupby("name").mean(numeric_only=True)
    print(new)
    return new
