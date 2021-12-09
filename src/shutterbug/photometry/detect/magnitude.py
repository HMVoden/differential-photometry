import logging
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import pandas as pd
from shutterbug.photometry.detect.detect import DetectBase


@dataclass
class MagnitudeDetector(DetectBase):

    star_medians: pd.Series

    def __init__(self, ds, **kwargs):
        logging.debug("Setting up magnitude detector")
        super().__init__(**kwargs)
        self.star_medians = ds.groupby("name").agg({"mag": "median"})
        self.detector_name = "Magnitude"
        self.detector_units = "mag"
        self.log()

    def detect(self, target_star: str) -> npt.NDArray[np.str_]:
        """Locates all stars that within a tolerance around a target star's magnitude

        Parameters
        ----------
        ds : xr.Dataset
            Already cleaned dataset
        tolerance : float
            The amount to add to a star's median
        target : str
            Target star's name

        Returns
        -------
        npt.NDArray
            Numpy array of all the star's names that this found

        """
        medians = self.star_medians
        tolerance = self.tolerance
        target_index = medians.index.get_loc(target_star)
        target_median = medians.iloc[target_index]
        distance_from_target = np.abs(medians - target_median)
        result_stars = medians[distance_from_target <= tolerance].dropna().index
        logging.debug(
            f"Found stars within magnitude tolerance: {', '.join(result_stars)}"
        )
        return result_stars
