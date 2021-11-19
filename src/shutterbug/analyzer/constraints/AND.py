from typing import Iterable, Sequence, Tuple

from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class ANDConstraint(ConstraintInterface):
    constraints: Iterable[ConstraintInterface]

    def __init__(self, *constraints: Tuple[ConstraintInterface]):
        if len(constraints) < 2:
            raise ValueError("Not enough constraints given for AND")
        self.constraints = list(*constraints)

    def meets(self, values: Sequence) -> Iterable[int]:
        good_indices = set(range(0, len(values)))
        for con in self.constraints:
            met_indices = set(con.meets(values))
            good_indices = good_indices.intersection(met_indices)
            # If we're at 0 no need to continue
            if len(good_indices) == 0:
                break
        return good_indices
