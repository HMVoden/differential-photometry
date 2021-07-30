import pandas as pd
import xarray as xr
import pytest

from importlib.resources import files

import tests.datasets.single as single
import tests.datasets.double as double
import tests.datasets.raw as raw

raw = [x for x in files(raw).iterdir() if x.suffix == ".csv"]
single = [x for x in files(single).iterdir() if x.suffix == ".csv"]
double = [x for x in files(double).iterdir() if x.suffix == ".csv"]


@pytest.fixture(scope="session", params=raw)
def raw_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=single)
def single_night_test_data(request):
    yield pd.read_csv(request.param).to_xarray()


@pytest.fixture(scope="session", params=double)
def dual_night_test_data(request):
    yield pd.read_csv(request.param).to_xarray()
