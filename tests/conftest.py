from importlib.resources import files

import pandas as pd
import pytest
import xarray as xr

import tests.datasets.double as double
import tests.datasets.duplicates as dup
import tests.datasets.raw as raw
import tests.datasets.single as single

raw = [x for x in files(raw).iterdir() if x.suffix == ".csv"]
single = [x for x in files(single).iterdir() if x.suffix == ".csv"]
double = [x for x in files(double).iterdir() if x.suffix == ".csv"]
duplicates = [x for x in files(dup).iterdir() if x.suffix == ".csv"]


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
