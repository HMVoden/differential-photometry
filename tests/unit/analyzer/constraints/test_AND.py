from typing import Iterable, Sequence

import pytest
from hypothesis import given
from hypothesis.strategies import floats, lists
from shutterbug.analyzer.constraints.AND import ANDConstraint
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface
from tests.unit.analyzer.constraints.hypothesis_constraints import constraints


@given(lists(floats(allow_nan=False, allow_infinity=False)), constraints(min_size=2))
def test_And_Constraint(
    data: Sequence[float], constraints: Iterable[ConstraintInterface]
):
    AND = ANDConstraint(*constraints)
    expected = set(range(0, len(data)))
    for con in constraints:
        expected = set(expected.intersection(con.meets(data)))
    actual = set(AND.meets(data))
    assert expected == actual


@given(
    constraints(min_size=0, max_size=1),
)
def test_AND_not_enough_constraints(constraints):
    with pytest.raises(ValueError):
        AND = ANDConstraint(*constraints)
