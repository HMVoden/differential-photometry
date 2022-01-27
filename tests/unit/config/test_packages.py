from shutterbug.config.packages import (
    to_folder,
    PhotometryConfig,
)

from hypothesis import given
from hypothesis.strategies import floats, lists, one_of, none
from pathlib import Path


def test_to_folder_str():
    folder = Path("~/test")
    expanded = folder.expanduser()
    as_str = str(folder)
    assert to_folder(as_str) == expanded


def test_to_folder_path():
    folder = Path("~/test")
    expanded = folder.expanduser()
    assert to_folder(folder) == expanded


@given(
    lists(
        one_of(floats(min_value=0, allow_nan=False, allow_infinity=False), none()),
        min_size=2,
        max_size=2,
    )
)
def test_fromdict(mag_dist):
    mag, dist = mag_dist

    con = PhotometryConfig.fromdict(
        **{"magnitude_limit": mag, "distance_limit": dist, "extra": "test"}
    )
    default = PhotometryConfig()
    if mag != None:
        assert con.magnitude_limit == mag
    else:
        assert con.magnitude_limit == default.magnitude_limit
    if dist != None:
        assert con.distance_limit == dist
    else:
        assert con.distance_limit == default.distance_limit


@given(
    floats(min_value=0, allow_infinity=False, allow_nan=False),
    floats(min_value=0, allow_infinity=False, allow_nan=False),
)
def test_asdict(mag, dist):

    con = PhotometryConfig(magnitude_limit=mag, distance_limit=dist)
    returned = con.asdict

    assert returned["magnitude_limit"] == mag
    assert returned["distance_limit"] == dist
