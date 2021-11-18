from typing import Iterable, Sequence

from hypothesis.strategies import composite, floats, lists
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface


class GreaterThanConstraint(ConstraintInterface):
    constraint: float

    def __init__(self, greater_than_num: float):
        self.constraint = greater_than_num

    def meets(self, values: Sequence[float]) -> Iterable[int]:
        meets_constraint = []
        for idx, val in enumerate(values):
            if val > self.constraint:
                meets_constraint.append(idx)
        return set(meets_constraint)


class LessThanConstraint(ConstraintInterface):
    constraint: float

    def __init__(self, less_than_num: float):
        self.constraint = less_than_num

    def meets(self, values: Sequence[float]) -> Iterable[int]:
        meets_constraint = []
        for idx, val in enumerate(values):
            if val < self.constraint:
                meets_constraint.append(idx)
        return set(meets_constraint)


@composite
def constraints(draw, min_size=0, max_size=None):
    lt_constraints = draw(
        lists(
            floats(allow_nan=False, allow_infinity=False),
            min_size=min_size,
            max_size=max_size,
        )
    )
    min_size = max(0, (min_size - len(lt_constraints)))
    if max_size is not None:
        max_size = min(0, max_size - len(lt_constraints))
    # so we don't go over our maximums or under our minimums
    gt_constraints = draw(
        lists(
            floats(allow_nan=False, allow_infinity=False),
            min_size=min_size,
            max_size=max_size,
        )
    )
    constraints = []
    for lt_num in lt_constraints:
        constraints.append(LessThanConstraint(lt_num))
    for gt_num in gt_constraints:
        constraints.append(GreaterThanConstraint(gt_num))
    return constraints
