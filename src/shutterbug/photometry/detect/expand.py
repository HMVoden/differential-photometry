import functools
import logging
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import numpy.typing as npt
import xarray as xr
from shutterbug.photometry.detect.distance import DistanceDetector
from shutterbug.photometry.detect.magnitude import MagnitudeDetector


@dataclass
class ExpandingConditionalDetector:
    minimum_stars: int
    max_iterations: int
    magnitude_detector: MagnitudeDetector
    distance_detector: DistanceDetector

    def detect(
        self, non_varying_stars: xr.DataArray, target_star: str
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
            return non_varying_stars.star.values

        matching_stars = np.array([])  # so linter doesn't complain
        i = 0
        while i < self.max_iterations:
            nearby_stars = distance_detector.detect(target_star)
            matching_stars = functools.reduce(
                np.intersect1d, (mag_stars, nearby_stars, non_varying_stars.values)
            )
            if matching_stars.size >= minimum_stars + 1:  # no more work required
                # +1 as results always include target star
                break
            elif i == (self.max_iterations - 1):
                raise RuntimeError(
                    """Unable to find minimum number of stars with set distance and magnitude
                    requirements, exiting program"""
                )
            self.max_iterations -= 1
            distance_detector.expand

            # end while loop
        return matching_stars
