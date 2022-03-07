from typing import List, Protocol

from shutterbug.data import Star


class Photometer(Protocol):
    def average_differential(self, target: Star, reference: List[Star]):
        ...
