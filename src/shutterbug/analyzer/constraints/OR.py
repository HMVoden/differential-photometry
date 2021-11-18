from typing import Iterable, Sequence, Tuple

from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class ORConstraint(ConstraintInterface):
    constraints: Iterable[ConstraintInterface]

    def __init__(self, *constraints: Tuple[ConstraintInterface]):
        if len(constraints) < 2:
            raise ValueError("Not enough constraints given for OR")
        self.constraints = list(constraints)

    def meets(self, values: Sequence) -> Iterable[int]:
        good_indices = set()
        for con in self.constraints:
            met_indices = set(con.meets(values))
            good_indices = good_indices.union(met_indices)
        return good_indices
