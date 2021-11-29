from typing import Dict, List

import hypothesis.strategies as st
import numpy as np
import pytest
from hypothesis import given
from hypothesis.extra.pandas import column, data_frames
from shutterbug.sanitizer.sanitize import sanitize


@pytest.mark.parametrize(
    "numeric_columns",
    [
        ["Data_1", "Data_2", "Data_3", "$MetaData_1"],
        ["data1", "data2", "data3", "metadata1"],
    ],
)
@given(
    pandas_frame=data_frames(
        columns=[
            column(name="Data_1", elements=st.floats(allow_infinity=False)),
            column(name="Data_2", elements=st.floats(allow_infinity=False)),
            column(name="Data_3", elements=st.floats(allow_infinity=False)),
            column(name="$MetaData_1", elements=st.floats(allow_infinity=False)),
            column(name="$MetaData_2", elements=st.text()),
            column(name="$MetaData_3", elements=st.datetimes(allow_imaginary=False)),
        ]
    )
)
def test_sanitize_with_pandas(pandas_frame, numeric_columns):
    primary_columns = ["data1", "data2", "data3"]
    cleaned_frame = sanitize(
        frame=pandas_frame,
        primary_variables=primary_columns,
        numeric_variables=numeric_columns,
    )
    expected_column_names = primary_columns.extend(
        ["metadata1", "metadata2", "metadata3"]
    )
    assert set(expected_column_names) == set(cleaned_frame.columns)
    for numeric_col in numeric_columns:
        assert np.count_nonzero(np.isnan(numeric_col)) == 0


@pytest.mark.parametrize(
    "numeric_variables",
    [
        ["Data_1", "Data_2", "Data_3", "$MetaData_1"],
        ["data1", "data2", "data3", "metadata1"],
    ],
)
@given(
    xarray_dataset=data_frames(
        columns=[
            column(name="Data_1", elements=st.floats(allow_infinity=False)),
            column(name="Data_2", elements=st.floats(allow_infinity=False)),
            column(name="Data_3", elements=st.floats(allow_infinity=False)),
            column(name="$MetaData_1", elements=st.floats(allow_infinity=False)),
            column(name="$MetaData_2", elements=st.text()),
            column(name="$MetaData_3", elements=st.datetimes(allow_imaginary=False)),
        ]
    )
)
def test_sanitize_with_xarray(xarray_dataset, numeric_variables):
    xarray_dataset = xarray_dataset.to_xarray()
    primary_variables = ["data1", "data2", "data3"]
    cleaned_set = sanitize(
        frame=xarray_dataset,
        primary_variables=primary_variables,
        numeric_variables=numeric_variables,
    )
    expected_variable_names = primary_variables.extend(
        ["metadata1", "metadata2", "metadata3"]
    )
    assert set(expected_variable_names) == set(cleaned_set.keys())
    for numeric_col in numeric_variables:
        assert np.count_nonzero(np.isnan(numeric_col)) == 0


def test_sanitize_duplicates_error():
    with pytest.raises(ValueError):
        sanitize(1, [], discard_variables=[], keep_variables=[])


def test_sanitize_duplicates_wrong_setting():
    with pytest.raises(ValueError):
        sanitize(1, [], keep_duplicates="potato")


def test_sanitize_empty_primary():
    with pytest.raises(ValueError):
        sanitize(1, [])


def test_sanitize_wrong_dataframe():
    with pytest.raises(ValueError):
        sanitize(1, ["test"])
