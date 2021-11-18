import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.numpy import array_shapes, arrays
from hypothesis.strategies import composite, floats
from shutterbug.analyzer.differential import DifferentialPhotometryCalculator


@composite
def target_and_reference(draw):
    target = draw(
        arrays(
            dtype=float,
            elements=floats(allow_nan=False, allow_infinity=False),
            shape=array_shapes(min_dims=1, max_dims=1),
        )
    )
    reference = draw(
        arrays(
            dtype=float,
            elements=floats(allow_nan=False, allow_infinity=False),
            shape=(len(target), 1),
        )
    )
    return target, reference


@given(target_and_reference())
def test_differential_calculation(data):
    calc = DifferentialPhotometryCalculator()
    target, reference = data
    expected = np.mean((reference - target), axis=0)
    actual = calc.differential(target, reference, axis=0)
    assert all(np.isclose(actual, expected))


@given(target_and_reference())
def test_differential_error_calculation(data):
    calc = DifferentialPhotometryCalculator()
    target, reference = data
    N = reference.shape[0] + 1

    expected = np.sqrt(np.sum((target ** 2 + reference ** 2), axis=0)) / N
    actual = calc.differential_error(target, reference, axis=0)
    assert all(np.isclose(actual, expected))
