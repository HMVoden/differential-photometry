from dataclasses import dataclass
import logging
import numpy as np
import shutterbug.photometry.detect.variation as variation
import shutterbug.photometry.differential as diff
import xarray as xr
from shutterbug.photometry.detect.expand import ExpandingConditionalDetector
import shutterbug.ux.progress_bars as bars


@dataclass
class IntradayDifferential:
    iterations: int
    expanding_detector: ExpandingConditionalDetector
    stationarity_tester: variation.StationarityTestStrategy

    def differential_photometry(self, ds: xr.Dataset) -> xr.Dataset:
        logging.info("Starting differential photometry")
        flag = self.stationarity_tester.varying_flag
        ds.coords[flag] = ("star", np.full(ds["star"].size, False))
        non_varying = ds  # all stars non-varying to start
        bars.xarray(
            name="star_phot", desc="Intraday", unit="star", leave=False, indentation=2
        )
        it_bar = bars.build(
            "iteration", "Iteration", "iteration", self.iterations, False, 1
        )
        with it_bar as pbar:
            for _ in range(self.iterations):
                ds = ds.groupby("star").progress_map(
                    self._per_star, non_varying=non_varying
                )
                ds[flag] = ds[flag].groupby("star").any(...)
                non_varying = ds.where(ds[flag] == False, drop=True)
                pbar.update()

        logging.info("Finished differential photometry")

        return ds

    def _per_star(self, day_star: xr.Dataset, non_varying: xr.Dataset):
        stationarity_tester = self.stationarity_tester
        detector = self.expanding_detector
        non_varying_stars = non_varying.star.values
        target_star = day_star["star"].values
        nearby_star_names = detector.detect(
            target_star=target_star, non_varying_stars=non_varying_stars
        )

        nearby_reference_stars = non_varying.sel(star=nearby_star_names)

        nearby_reference_stars = nearby_reference_stars.where(
            ~(nearby_reference_stars.star == target_star), drop=True
        )
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
