import numpy as np
import pytest
import xarray as xr
from hypothesis import given
from hypothesis.strategies import composite, floats, integers, lists
from shutterbug.analyzer.constraints.distance import DistanceConstraint


@composite
def xy_dataset(draw):
    xs = draw(
        lists(
            floats(min_value=0, allow_nan=False, allow_infinity=False),
            unique=True,
            min_size=1,
        )
    )
    ys = draw(
        lists(
            floats(min_value=0, allow_nan=False, allow_infinity=False),
            unique=True,
            max_size=len(xs),
            min_size=len(xs),
        )
    )
    stars = []
    for i in range(len(xs)):
        stars.append(f"star{i}")
    ds = xr.Dataset(
        coords={"star": stars},
        data_vars={"x": (["star"], xs), "y": (["star"], ys)},
    )
    return ds


@given(xy_dataset(), floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_distance_constraint(data, radius):
    constraint = DistanceConstraint(radius)

    within_radius = data.where(np.sqrt(data.x ** 2 + data.y ** 2) <= radius, drop=True)[
        "star"
    ].values

    expected = within_radius.sort()
    actual_idx = constraint.meets(data)
    actual = data.star.values[actual_idx].sort()
    assert expected == actual


@given(floats(max_value=-1, allow_nan=False, allow_infinity=False))
def test_minimum_radius(radius):
    with pytest.raises(ValueError):
        DistanceConstraint(radius)
