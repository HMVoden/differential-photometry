# import numpy as np
# import pandas as pd
# import pytest
# import shutterbug.data.sanitize as sanitize
# from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype

# required_cols = ["obj", "name", "mag", "error", "x", "y", "jd"]


# @pytest.fixture()
# def pre_cleaned(raw_test_data):
#     cleaned = sanitize.drop_and_clean_names(raw_test_data, required_cols)
#     cleaned = sanitize.add_time_information(cleaned, "jd")
#     cleaned = sanitize.clean_data(cleaned, ["star", "x", "y", "jd", "time"])
#     cleaned = sanitize.remove_nan_stars(cleaned)
#     cleaned = sanitize.remove_wrong_count_stars(cleaned)
#     cleaned = sanitize.drop_duplicate_time(cleaned)
#     yield cleaned


# @pytest.fixture()
# def pre_cleaned_duplicates(dup_test_data):
#     cleaned = sanitize.drop_and_clean_names(dup_test_data, required_cols)
#     cleaned = sanitize.add_time_information(cleaned, "jd")
#     cleaned = sanitize.clean_data(cleaned, ["star", "x", "y", "jd", "time"])
#     yield cleaned


# @pytest.mark.parametrize(
#     "cols",
#     [
#         ["jd"],
#         ["jd", "x"],
#         ["jd", "name", "y"],
#         ["jd", "mag", "x", "y", "s-n", "error", "name"],
#     ],
# )
# def test_drop_and_clean_names(raw_test_data, cols):
#     clean_names = sanitize.drop_and_clean_names(raw_test_data, cols)
#     cols = ["star" if ("name" == x) or ("obj") == x else x for x in cols]
#     assert set(cols) == set(clean_names.keys())


# @pytest.mark.parametrize(
#     "coord_names",
#     [
#         ["jd"],
#         ["jd", "x"],
#         ["jd", "star", "y"],
#         ["jd", "mag", "x", "y", "error", "star"],
#     ],
# )
# def test_clean_data_coords(raw_test_data, coord_names):
#     cleaned = sanitize.drop_and_clean_names(raw_test_data, required_cols)
#     cleaned = sanitize.clean_data(cleaned, coord_names)
#     coord_names.append("index")
#     coord_keys = list(cleaned.coords.keys())
#     assert all(x in coord_keys for x in coord_keys)


# def test_clean_data_values(pre_cleaned):
#     cleaned = pre_cleaned
#     assert is_numeric_dtype(cleaned["mag"].values)
#     assert is_numeric_dtype(cleaned["error"].values)
#     assert is_datetime64_any_dtype(cleaned["time"].values)


# def test_drop_duplicate_time(pre_cleaned_duplicates):
#     initial_size = pre_cleaned_duplicates["index"].size
#     initial_star_num = pre_cleaned_duplicates["star"].size
#     initial_time_num = pre_cleaned_duplicates["time"].size
#     # TODO improve these tests with more specific parameters
#     dedup = sanitize.drop_duplicate_time(pre_cleaned_duplicates)
#     assert dedup["index"].size < initial_size
#     assert dedup["star"].size < initial_star_num
#     assert dedup["time"].size < initial_time_num


# def test_arrange_star_time(pre_cleaned):
#     data = pre_cleaned
#     num_stars = np.unique(data["star"]).size
#     num_time = np.unique(data["time"]).size
#     data = sanitize.arrange_star_time(data)
#     assert set(data.dims.keys()) == {"star", "time"}
#     assert data.indexes["star"].size == num_stars
#     assert data.indexes["time"].size == num_time
#     assert data["x"].size == data["star"].size
#     assert data["y"].size == data["star"].size


# @pytest.mark.parametrize(
#     "test_in, expected",
#     [
#         ("M3-12", ["M3-12"]),
#         ("M3-12 M3-14 M3-15 M3-27", ["M3-12", "M3-14", "M3-15", "M3-27"]),
#         ("M3-12,M3-14,M3-15,M3-27", ["M3-12", "M3-14", "M3-15", "M3-27"]),
#         ("M3-12, M3-14, M3-15, M3-27", ["M3-12", "M3-14", "M3-15", "M3-27"]),
#     ],
# )
# def test_to_remove_to_list(test_in, expected):
#     split = set(sanitize.to_remove_to_list(test_in))
#     print(split)
#     assert set(expected) == split


# def test_remove_stars(pre_cleaned):
#     remove_stars = list(pre_cleaned["star"].values[0])
#     cleaned = sanitize.remove_stars(pre_cleaned, remove_stars)
#     assert remove_stars[0] not in cleaned["star"].values.tolist()


# def test_remove_nan_stars(pre_cleaned_duplicates):
#     initial_star_count = pre_cleaned_duplicates["star"].values.size
#     cleaned = sanitize.remove_nan_stars(pre_cleaned_duplicates)
#     assert cleaned["star"].values.size < initial_star_count


# def test_remove_wrong_count(pre_cleaned_duplicates):
#     initial_star_count = pre_cleaned_duplicates["star"].values.size
#     cleaned = sanitize.remove_wrong_count_stars(pre_cleaned_duplicates)
#     assert cleaned["star"].values.size < initial_star_count


# @pytest.mark.parametrize("stars_to_remove", [[]])
# def test_remove_incomplete(pre_cleaned_duplicates, stars_to_remove):
#     data = pre_cleaned_duplicates
#     initial_star_count = np.unique(data["star"]).size
#     initial_time_count = np.unique(data["time"]).size
#     data = sanitize.remove_incomplete_stars(data, stars_to_remove)
#     assert np.unique(data["star"]).size < initial_star_count
#     assert np.unique(data["time"]).size <= initial_time_count


# class TestCompare:
#     @pytest.mark.parametrize(
#         "data",
#         [
#             pytest.lazy_fixture("compare_single_test_data"),
#             pytest.lazy_fixture("compare_double_test_data"),
#         ],
#     )
#     def test_compare_columns(self, data):
#         raw, good = data
#         data = sanitize.drop_and_clean_names(raw, required_cols)
#         data = sanitize.add_time_information(data, "jd")
#         data = sanitize.clean_data(data, ["star", "x", "y", "jd", "time"])
#         data = sanitize.remove_nan_stars(data)
#         data = sanitize.remove_wrong_count_stars(data)
#         data = sanitize.drop_duplicate_time(data)
#         good = sanitize.drop_and_clean_names(
#             good, ["mag", "error", "x", "y", "star", "jd", "time"]
#         )
#         good = good.set_coords(["star", "time", "x", "y"])
#         data = data.drop_vars("jd")  # not in 'clean' set
#         mag_delta = np.around((data.mag.values - good.mag.values).sum(), decimals=4)
#         error_delta = np.around(
#             (data.error.values - good.error.values).sum(), decimals=4
#         )
#         assert mag_delta == 0.0
#         assert error_delta == 0.0
#         assert (data.star.values == good.star.values).all()
