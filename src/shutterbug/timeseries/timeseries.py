import logging
from typing import List

import numpy as np
import pandas as pd
import xarray as xr
from astropy.stats import sigma_clip


def sigma_clip_data(
    data: List[float], stat_func, error: List[float] = None
) -> pd.DataFrame:

    sample = sigma_clip(data, sigma=3, masked=True)
    if error is not None:
        error = np.ma.array(error, mask=sample.mask)
        return stat_func(sample, error)
    return stat_func(sample)
