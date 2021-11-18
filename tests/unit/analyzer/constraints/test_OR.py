from typing import Iterable, Sequence

import pytest
from hypothesis import given
from hypothesis.strategies import floats, lists
from shutterbug.analyzer.constraints.OR import ORConstraint
from shutterbug.analyzer.core.interface.constraints import ConstraintInterface
from tests.unit.analyzer.constraints.hypothesis_constraints import constraints


@given(lists(floats(allow_nan=False, allow_infinity=False)), constraints(min_size=2))
def test_OR(data: Sequence[float], constraints: Iterable[ConstraintInterface]):
    OR = ORConstraint(*constraints)
    expected = set()
    for con in constraints:
        expected = set(expected.union(con.meets(data)))
    actual = set(OR.meets(data))
    assert expected == actual


@given(
    constraints(min_size=0, max_size=1),
)
def test_OR_not_enough_constraints(constraints):
    with pytest.raises(ValueError):
        OR = ORConstraint(*constraints)
