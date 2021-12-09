import functools
import logging
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import numpy.typing as npt
import pandas as pd
from shutterbug.photometry.detect.distance import DistanceDetector
from shutterbug.photometry.detect.magnitude import MagnitudeDetector


@dataclass
class ExpandingConditionalDetector:
    minimum_stars: int
    max_iterations: int
    magnitude_detector: MagnitudeDetector
    distance_detector: DistanceDetector

    def detect(
        self,
        target_star: str,
        non_varying_stars: npt.NDArray[np.str_],
    ) -> npt.NDArray[np.str_]:
        """Starting at an initial distance, finds nearby stars. If not enough stars are
        found, determined by minimum stars, expands the search. If unable to find
        enough stars, this will error out.

        Parameters
        ----------
        ds : xr.Dataset
            Clean dataset with x-y coordinates and stars

        Returns
        -------
        Tuple[npt.NDArray, float]
            numpy array of all stars found and the radius they were found in

        Raises
        ------
        RuntimeError
            If not enough stars are found, then this star will break differential
            photometry and thus the program cannot continue without its an increase in tolerances.

        """
        mag_stars = self.magnitude_detector.detect(target_star)
        minimum_stars = self.minimum_stars
        distance_detector = self.distance_detector

        if mag_stars.size <= minimum_stars:
            return non_varying_stars

        # i = 0
        # while i < self.max_iterations:
        nearby_stars = distance_detector.detect(target_star)
        matching_stars = functools.reduce(
            np.intersect1d, (mag_stars, nearby_stars, non_varying_stars)
        )
        # if matching_stars.size >= minimum_stars + 1:  # no more work required
        #     # +1 as results always include target star
        #     break
        # elif i == (self.max_iterations - 1):
        #     break
        # logging.debug(
        #     f"Failed to find sufficient stars, found {nearby_stars} distance stars and {mag_stars} magnitude stars, total {matching_stars.size}, for target star {target_star}",
        # )
        # raise RuntimeError(
        #     f"""Unable to find minimum number of stars with set distance and magnitude
        #     requirements. Required {minimum_stars}, found {matching_stars.size}, exiting program"""
        # )
        # self.max_iterations -= 1
        # logging.warning(
        #     f"Iteration {self.max_iterations + i} found {matching_stars.size} stars, expanding search by {distance_detector.increment} px to {distance_detector.tolerance + distance_detector.increment}"
        # )
        # distance_detector.expand()

        # end while loop
        if matching_stars.size <= 1:
            matching_stars = non_varying_stars
            logging.debug(
                f"{target_star}: no nearby stars in distance {distance_detector.tolerance} px and magnitude range {self.magnitude_detector.tolerance}, using all available non-varying stars as reference stars."
            )
        else:
            logging.debug(
                f"{target_star}: {matching_stars.size} non-varying reference stars in radius {distance_detector.tolerance} and magnitude tolerance {self.magnitude_detector.tolerance}"
            )
        if matching_stars.size == 1 or matching_stars.size == 0:
            raise RuntimeError
        return matching_stars
