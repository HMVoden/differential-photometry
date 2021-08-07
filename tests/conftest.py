from importlib.resources import files

import pandas as pd
import pytest
import shutterbug.data.sanitize as sanitize

import tests.datasets.double as double
import tests.datasets.duplicates as dup
import tests.datasets.raw as raw
import tests.datasets.single as single

raw = [x for x in files(raw).iterdir() if x.suffix == ".csv"]
single = [x for x in files(single).iterdir() if x.suffix == ".csv"]
double = [x for x in files(double).iterdir() if x.suffix == ".csv"]
duplicates = [x for x in files(dup).iterdir() if x.suffix == ".csv"]
raw_good_single = ((raw[1], single[0]), (raw[1], single[1]))
raw_good_double = ((raw[0], double[0]), (raw[0], double[1]))


@pytest.fixture(scope="session", params=raw)
def raw_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=single)
def single_night_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=double)
def dual_night_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=duplicates)
def dup_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=raw_good_single)
def compare_single_test_data(request):
    raw = pd.read_csv(request.param[0]).to_xarray()
    good = pd.read_csv(request.param[1]).to_xarray()
    yield (raw, good)


@pytest.fixture(scope="session", params=raw_good_double)
def compare_double_test_data(request):
    raw = pd.read_csv(request.param[0]).to_xarray()
    good = pd.read_csv(request.param[1]).to_xarray()
    yield (raw, good)


@pytest.fixture(scope="session", params=raw)
def clean_data(request):
    data = pd.read_csv(request.param).to_xarray()
    data = sanitize.drop_and_clean_names(
        data, required_data=["mag", "error", "x", "y", "jd", "name"]
    )
    data = sanitize.add_time_information(data, "jd")
    data = sanitize.clean_data(data, ["x", "y", "jd", "time", "star"])
    data = sanitize.drop_duplicate_time(data)
    data = sanitize.remove_incomplete_stars(data)
    data = sanitize.arrange_star_time(data)
    yield data
