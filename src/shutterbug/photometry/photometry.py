import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
import shutterbug.photometry.detect.variation as variation
import shutterbug.photometry.differential as diff
import shutterbug.ux.progress_bars as bars
from shutterbug.photometry.detect.expand import ExpandingConditionalDetector


@dataclass
class IntradayDifferential:
    iterations: int
    expanding_detector: ExpandingConditionalDetector
    stationarity_tester: variation.StationarityTestStrategy

    def differential_photometry(self, ds: pd.DataFrame) -> pd.DataFrame:
        logging.info("Starting differential photometry")
        flag = self.stationarity_tester.varying_flag
        ds[flag] = np.full(len(ds), False)
        non_varying = ds  # all stars non-varying to start
        # bars.xarray(
        #     name="star_phot", desc="Intraday", unit="name", leave=False, indentation=2
        # )
        # it_bar = bars.build(
        #     "iteration", "Iteration", "iteration", self.iterations, False, 1
        # )
        # with it_bar as pbar:
        for it in range(self.iterations):
            logging.info(f"Starting iteration {it+1}")
            ds = ds.groupby(["name"]).apply(self._per_star, non_varying=non_varying)
            ds[flag] = ds[["name", flag]].groupby("name").transform(any)
            non_varying = ds[ds[flag] == False]
            # pbar.update()

        logging.info("Finished differential photometry")

        return ds

    def _per_star(self, day_star: pd.DataFrame, non_varying: pd.DataFrame):
        stationarity_tester = self.stationarity_tester
        detector = self.expanding_detector
        non_varying_stars = non_varying["name"].values
        target_star = day_star.name
        logging.info(f"Starting photometry and testing on star {target_star}")
        nearby_star_names = detector.detect(
            target_star=target_star, non_varying_stars=non_varying_stars
        )

        nearby_reference_stars = non_varying[
            (non_varying["name"].isin(nearby_star_names))
            & (non_varying["name"] != target_star)
        ]
        day_star["reference_stars"] = len(nearby_reference_stars.groupby("name"))
        adm = np.mean(
            nearby_reference_stars.groupby(["name"])
            .apply(lambda x: x["mag"].values - day_star["mag"].values)
            .values
        )
        day_star["average_diff_mags"] = adm

        adu = np.sqrt(
            np.sum(
                nearby_reference_stars.groupby("name").apply(
                    lambda x: (x["error"].values ** 2 + day_star["error"].values ** 2)
                )
            )
        ) / (len(nearby_reference_stars.groupby("name")) + 1)

        day_star["average_uncertainties"] = adu
        day_star = day_star.groupby(day_star["jd"].dt.date).apply(
            stationarity_tester.test_dataset
        )
        return day_star
