import numpy as np
import pandas as pd
import pytest
import xarray as xr
from hypothesis import given
from hypothesis.strategies import composite, floats, lists
from shutterbug.analyzer.constraints.distance import DistanceConstraint


@composite
def xy_dataset(draw):
    xs = draw(
        lists(
            floats(min_value=0, max_value=8192, allow_nan=False, allow_infinity=False),
            unique=True,
            min_size=1,
        )
    )
    ys = draw(
        lists(
            floats(min_value=0, max_value=8192, allow_nan=False, allow_infinity=False),
            unique=True,
            max_size=len(xs),
            min_size=len(xs),
        )
    )
    stars = []
    for i in range(len(xs)):
        stars.append(f"star{i}")
    df = pd.DataFrame({"star": stars, "x": xs, "y": ys})
    return df


@given(xy_dataset(), floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_distance_constraint(data, radius):
    constraint = DistanceConstraint(radius=radius, xs=data["x"], ys=data["y"])

    xs = data["x"]
    ys = data["y"]
    nearby_per_star = []
    for x, y in zip(xs, ys):
        dist = np.sqrt((xs - x) ** 2 + (ys - y) ** 2)

        indices = dist[dist <= radius].index.to_list().sort()
        nearby_per_star.append(indices)

    expected = nearby_per_star
    actual_nearby = []
    for _, series in data.iterrows():
        actual_idx = constraint.meets(series)
        actual_nearby.append(actual_idx)
    actual = actual_nearby
    assert expected == actual


@given(floats(max_value=-1, allow_nan=False, allow_infinity=False))
def test_minimum_radius(radius):
    with pytest.raises(ValueError):
        DistanceConstraint(radius=radius, xs=[1], ys=[1])
