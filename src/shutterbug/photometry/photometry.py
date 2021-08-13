from dataclasses import dataclass

import numpy as np
import shutterbug.photometry.detect.variation as variation
import shutterbug.photometry.differential as diff
import xarray as xr
from shutterbug.photometry.detect.expand import ExpandingConditionalDetector


@dataclass
class IntradayDifferential:
    iterations: int
    expanding_detector: ExpandingConditionalDetector
    stationarity_tester: variation.StationarityTestStrategy

    def differential_photometry(self, ds: xr.Dataset) -> xr.Dataset:
        flag = self.stationarity_tester.varying_flag
        ds.coords[flag] = ("star", np.full(ds["star"].size, False))
        non_varying = ds
        # ds = ds.assign_coords(date=ds["time"].dt.date)
        # ds = ds.set_index({"date": "date"})
        # ds = ds.stack(day_star=("date", "star"))

        for i in range(self.iterations):
            ds = ds.groupby("star").map(self._per_star, non_varying=non_varying)
            non_varying = ds.where(ds[flag] == False, drop=True)

        # ds = ds.unstack("day_star")
        ds[flag] = ds[flag].groupby("star").any(...)

        # ds = ds.reset_index("date", drop=True)
        return ds

    def _per_star(self, day_star: xr.Dataset, non_varying: xr.Dataset):
        stationarity_tester = self.stationarity_tester
        detector = self.expanding_detector
        non_varying_stars = non_varying.star.values
        target_star = day_star["star"].values
        nearby_star_names = detector.detect(
            target_star=target_star, non_varying_stars=non_varying_stars
        )
        nearby_star_names = nearby_star_names[1:]
        # remove first, which will be our star index
        nearby_reference_stars = non_varying.sel(star=nearby_star_names)
        day_star["average_diff_mags"] = diff.data_array_magnitude(
            day_star.mag, nearby_reference_stars.mag
        )
        day_star["average_uncertainties"] = diff.data_array_uncertainty(
            day_star.error, nearby_reference_stars.error
        )
        day_star = day_star.groupby(
            "time.date", restore_coord_dims=True, squeeze=False
        ).map(stationarity_tester.test_dataset)
        return day_star
