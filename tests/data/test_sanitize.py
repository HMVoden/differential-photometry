import pytest
import shutterbug.data.sanitize as sanitize


required_cols = ["obj", "name", "mag", "error", "x", "y", "jd"]


@pytest.mark.parametrize(
    "cols",
    [
        ["jd"],
        ["jd", "x"],
        ["jd", "name", "y"],
        ["jd", "mag", "x", "y", "s-n", "error", "name"],
    ],
)
def test_drop_and_clean_names(raw_test_data, cols):
    clean_names = sanitize.drop_and_clean_names(raw_test_data, cols)
    cols = ["star" if ("name" == x) or ("obj") == x else x for x in cols]
    assert set(cols) == set(clean_names.keys())


@pytest.mark.parametrize(
    "coord_names",
    [
        ["jd"],
        ["jd", "x"],
        ["jd", "star", "y"],
        ["jd", "mag", "x", "y", "error", "star"],
    ],
)
def test_clean_data_coords(raw_test_data, coord_names):
    clean_names = sanitize.drop_and_clean_names(raw_test_data, required_cols)
    cleaned = sanitize.clean_data(clean_names, coord_names)
    coord_names.append("index")
    coord_keys = list(cleaned.coords.keys())
    assert all(x in coord_keys for x in coord_keys)


def test_incomplete_stars(dataset, desired):
    pass
