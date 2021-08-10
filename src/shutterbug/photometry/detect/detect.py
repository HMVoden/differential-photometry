from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import xarray as xr


@dataclass
class DetectBase(ABC):
    tolerance: float
    tolerance_increment: float
    incremented: int = field(default=0, init=False)

    @abstractmethod
    def detect(self, ds: xr.Dataset):
        pass

    def expand(self):
        self.tolerance += self.tolerance_increment
        self.incremented += 1

    def contract(self):
        self.tolerance -= self.tolerance_increment
        self.incremented -= 1

    def reset_increment(self):
        change = self.incremented
        tol_inc = self.tolerance_increment
        if change != 0:
            self.tolerance += (-1 * change) * tol_inc
            self.incremented = 0
