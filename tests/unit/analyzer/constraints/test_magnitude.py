import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis.strategies import composite, floats, lists
from shutterbug.analyzer.constraints.magnitude import MagnitudeConstraint


@composite
def mag_dataset(draw):
    mags = draw(
        lists(
            lists(
                floats(
                    min_value=-40,
                    max_value=40,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                min_size=1,
            ),
            min_size=1,
        )
    )

    stars = []
    for i in range(len(mags)):
        stars.append(f"star{i}")
    df = pd.DataFrame({"star": stars, "mag": mags})
    return df


@given(mag_dataset(), floats(min_value=0, allow_nan=False, allow_infinity=False))
def test_magnitude_constraint(data, mag_range):
    constraint = MagnitudeConstraint(
        radius=mag_range, magnitudes=data["mag"].to_numpy()[0]
    )
    for row in data["mag"]:
        data["median"] = np.median(row)
    medians = data["median"]
    expected = []
    for target_med in medians:
        res = (medians - target_med).values
        indices = np.argwhere(np.absolute(res) <= mag_range).sort()
        expected.append(indices)
    actual = []
    for _, series in data.iterrows():
        actual.append(constraint.meets(series).sort())
    assert expected == actual


@given(floats(max_value=-1, allow_nan=False, allow_infinity=False))
def test_minimum_radius(radius):
    with pytest.raises(ValueError):
        MagnitudeConstraint(radius=radius, magnitudes=[1])
