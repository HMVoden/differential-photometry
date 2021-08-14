from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import xarray as xr
from xarray.core.dataset import calculate_dimensions
from shutterbug.photometry.detect.detect import DetectBase


@dataclass
class MagnitudeDetector(DetectBase):

    star_medians: xr.DataArray
    star_upper: xr.DataArray
    star_lower: xr.DataArray

    def __init__(self, ds, **kwargs):
        super().__init__(**kwargs)
        self.star_medians = ds["mag"].groupby("star").median(...)
        self.detector_name = "Magnitude"
        self.detector_units = "mag"
        self.log()
        self.calculate_tolerance_range()

    def calculate_tolerance_range(self):
        self.star_upper = self.star_medians + self.tolerance
        self.star_lower = self.star_medians - self.tolerance

    def expand(self):
        super().expand()
        self.calculate_tolerance_range()

    def contract(self):
        super().contract()
        self.calculate_tolerance_range()

    def reset_increment(self):
        super().reset_increment()
        self.calculate_tolerance_range()

    def detect(self, target_star: str) -> npt.NDArray[np.str_]:
        """Locates all stars that are less than (brighter) a target star's median
        magnitude plus a tolerance

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
        upper = self.star_upper
        lower = self.star_lower
        target_median_plus_tolerance = upper.sel(star=target_star)
        target_median_minus_tolerance = lower.sel(star=target_star)
        cond_less_than = medians >= target_median_minus_tolerance
        cond_greater_than = medians <= target_median_plus_tolerance
        result_stars = medians.where(
            (cond_less_than & cond_greater_than), drop=True
        ).star.values
        return result_stars
