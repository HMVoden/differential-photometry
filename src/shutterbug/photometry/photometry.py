from abc import ABC, abstractmethod
from typing import Callable

import numpy.typing as npt
import shutterbug.photometry.differential as differential
import xarray as xr
from shutterbug.photometry.detect.variation import VariationDetector


class DifferentialBase(ABC):
    varying_flag: str
    variation_detector: VariationDetector

    def __init__(self, varation_detector: VariationDetector):
        self.variation_detector = varation_detector

    def differential_photometry(self, ds: xr.Dataset) -> xr.Dataset:
        ds = differential.dataset(ds.groupby(self.varying_flag))
        return ds

    @abstractmethod
    def test_stationarity(self, ds: xr.Dataset) -> xr.Dataset:
        pass
