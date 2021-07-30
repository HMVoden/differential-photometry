import logging
from typing import Any, List

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype, CategoricalDtype

columns_check_function = {
    "mag": is_numeric_dtype,
    "error": is_numeric_dtype,
    "time": is_datetime64_any_dtype,
}

columns_fix_function = {
    "mag": pd.to_numeric,
    "error": pd.to_numeric,
    "time": pd.to_datetime,
}


def check_and_coerce_column(data: List[Any]) -> List[Any]:
    name = data.name
    if not columns_check_function[name](data):
        logging.warning(
            "Data column '%s' is not the proper type, attempting to fix", name
        )
        data = columns_fix_function[name](data, errors="coerce")
    return data


def clean_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Ensures that the columns mag, error, error_t and either obj or name are present.
    Then makes sure that the mag, error and error_t are viable and in the right format.
    Removes all stars with any mag value of "Flux<0"

    Parameters
    ----------
    dataframe : pd.DataFrame
        Dataframe to be cleaned, may have improper values

    Returns
    -------
    pd.DataFrame
        Clean dataframe

    Raises
    ------
    KeyError
        Error if the dataframe passed in is lacking critical columns
    KeyError
        Error if the dataframe passed in is lacking either a name or an obj column
    """
    if "obj" in dataframe.columns:
        dataframe = dataframe.rename(columns={"obj": "id"})
    if "name" in dataframe.columns:
        dataframe = dataframe.rename(columns={"name": "id"})

    required_columns = ["mag", "error", "time"]
    dataframe[required_columns] = dataframe[required_columns].apply(
        check_and_coerce_column
    )
    dataframe = dataframe.dropna()
    # Reduce memory footprint
    dataframe["id"] = dataframe["id"].astype(CategoricalDtype(dataframe["id"].unique()))
    dataframe["y_m_d"] = dataframe["y_m_d"].astype("category")
    dataframe[["mag", "error"]] = dataframe[["mag", "error"]].apply(
        pd.to_numeric, downcast="float"
    )
    dataframe = dataframe.drop_duplicates()
    return dataframe


def remove_incomplete_sets(
    df: pd.DataFrame, stars_to_remove: list[str] = []
) -> List[float]:
    """Founds the most common row counts by virtue of the star names in the dataset
    then removes any stars that do not have the same amount as the most common row count

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to be cleaned, must contain "id" column

    Returns
    -------
    pd.DataFrame
        Dataframe cleaned
    """
    row_counts = df["id"].value_counts()
    # most common value
    row_mode = row_counts.mode(dropna=True)[0]
    bad_stars = row_counts[row_counts != row_mode].index.values.tolist()
    if len(bad_stars) > 0:
        logging.warning(
            "Stars %s have been found without sufficient amount of information",
            bad_stars,
        )

    stars_to_remove.extend(bad_stars)
    remove_indices = df[df["id"].isin(stars_to_remove)].index
    df = df.drop(remove_indices)
    df["id"] = df.id.cat.remove_unused_categories()
    logging.info("Removed stars: %s", stars_to_remove)
    logging.info("Removed star count %s", len(stars_to_remove))
    return df


def to_remove_to_list(to_remove: str) -> List[str]:
    if to_remove is not None:
        if "," in to_remove:
            to_remove.str.replace(" ", "")
            to_remove = to_remove.split(",")
        else:
            to_remove = to_remove.split(" ")
    else:
        to_remove = []
    return to_remove


# def remove_specified_stars(df: pd.DataFrame,
#                            to_remove: List[str] = None) -> pd.DataFrame:

#         logging.info("Attempting to remove stars: %s", to_remove)
#         try:
#             star_rows = df[df["id"].isin(bad_stars)].index
#             if len(star_rows) == 0:
#                 logging.warning(
#                     "No stars with specified names exist in dataset")
#                 logging.warning("Continuing without star removal")
#             else:
#                 df = df.drop(index=star_rows)
#                 logging.info("Removed stars: %s", bad_stars)
#             del star_rows
#             gc.collect()
#         except KeyError as e:
#             logging.error("Failed to remove specified stars")
#             logging.error("Error received: %s", e)
#             logging.warning("Continuing without star removal")
#     return df


def clean_headers(header: str) -> str:
    header = (
        header.strip()
        .lower()
        .replace(" ", "_")
        .replace("(", "_")
        .replace(")", "")
        .replace("<", "")
        .replace(">", "")
    )
    # Cleanup of headers, could be made more succinct with a simple REGEX or two

    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this function.
    # Finds common column names
    return header
