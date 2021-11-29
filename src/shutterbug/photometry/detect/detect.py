from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging
import xarray as xr


@dataclass
class DetectBase(ABC):
    detector_name: str = field(init=False)
    detector_units: str = field(init=False)
    tolerance: float
    increment: float
    incremented: int = field(default=0, init=False)

    @abstractmethod
    def detect(self, ds: xr.Dataset):
        pass

    def expand(self):
        logging.debug(
            f"{self.detector_name} expanding from {self.tolerance} to {self.tolerance + self.increment} {self.detector_units}"
        )
        self.tolerance += self.increment
        self.incremented += 1

    def contract(self):
        logging.debug(
            f"{self.detector_name} contracting from {self.tolerance} {self.detector_units} to {self.tolerance + self.increment} {self.detector_units}"
        )
        self.tolerance -= self.increment
        self.incremented -= 1

    def reset_increment(self):
        change = self.incremented
        tol_inc = self.increment
        if change != 0:
            self.tolerance += (-1 * change) * tol_inc
            self.incremented = 0
        logging.debug(
            f"{self.detector_name} reset to tolerance {self.tolerance} {self.detector_units}"
        )

    def log(self):
        detector_name = self.detector_name
        logging.info(
            f"{detector_name} detector initialized with tolerance {self.tolerance} {self.detector_units} and increment {self.increment} {self.detector_units}"
        )
