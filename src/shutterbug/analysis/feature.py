from attr import define, field
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

# std dev and weighted version

# MAD

# IQR (for skewed distributions like an eclipsing binary)

# RoMS (Robust Median Statistic)


class FeatureBase(ABC):
    name: str = field(init=False)

    @abstractmethod
    def __call__(self, data: pd.Series) -> float:
        raise NotImplementedError


@define
class IQR(FeatureBase):
    """Calculates the IQR of a given dataset"""

    name = "IQR"

    def __call__(self, data: pd.Series) -> float:
        q3 = data.quantile(q=0.75)
        q1 = data.quantile(q=0.25)
        # Return as only single value
        IQR = (q3 - q1).to_numpy()[0]
        return IQR


@define
class InverseVonNeumann(FeatureBase):
    """Calculates the inverse Von Neumann statistic on a given dataset"""

    name = "Inverse Von Neumann"

    def __call__(self, data: pd.Series) -> float:
        if len(data) < 2:
            raise ValueError(
                "The Von Neumann test requires more than two numbers to operate"
            )
        numbers = data.to_numpy()
        i_plus_1 = numbers[1:]  # Get all numbers past the first
        i = numbers[:-1]  # Get all numbers until the last
        d = np.sum(i_plus_1 - i) ** 2 / len(i)
        s = np.var(numbers, ddof=1)  # sample variance
        return s / d
