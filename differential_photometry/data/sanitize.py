import logging
from typing import List

import numpy as np
import pandas as pd


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

    required_columns = ["mag", "error", "jd", "id"]
    for col in required_columns:
        if col not in dataframe.columns:
            raise KeyError(
                "Unable to continue program, missing critical column: {0}".
                format(col))

    datatypes = dataframe.dtypes
    if not (datatypes.mag.name
            == "float64"):  # Could make this apply to error and error_t too
        logging.warning(
            "Data column '%s' is not a numerical type, attempting to fix",
            "mag")
        # First instance of bad data
        bad_mags = dataframe[(dataframe.mag == "Flux<0")]

        stars_removed = bad_mags.id.unique()
        star_rows = dataframe[(dataframe["id"].isin(stars_removed))]

        logging.warning(
            "Removing star(s) {0} from dataset".format(stars_removed))
        dataframe = dataframe.drop(index=star_rows.index)
        dataframe["mag"] = pd.to_numeric(dataframe["mag"])

    return dataframe


def remove_incomplete_sets(df: pd.DataFrame) -> pd.DataFrame:
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
    row_mode = row_counts.mode()[0]
    bad_stars = row_counts[row_counts != row_mode].index.values
    if len(bad_stars) > 0:
        logging.warning(
            "Stars have been found without sufficient amount of information")
        logging.warning("Removing star(s) %s from dataset", bad_stars)
        star_rows = df[df["id"].isin(bad_stars)]
        df = df.drop(index=star_rows.index)
    return df


def remove_specified_stars(df: pd.DataFrame,
                           to_remove: List[str] = None) -> pd.DataFrame:
    if to_remove is not None:
        if isinstance(to_remove, list):
            # Assume it's laid out correctly already
            star_rows = df[df["id"].isin(to_remove)]
        elif isinstance(to_remove, str):
            # Space or comma+space separated
            if ',' in to_remove:
                to_remove.str.replace(" ", "")
                bar_stars = to_remove.split(",")
            else:
                bad_stars = to_remove.split(" ")
        # end ifs
        logging.info("Attempting to remove stars: %s", bad_stars)
        try:
            star_rows = df[df["id"].isin(bad_stars)].index
            if len(star_rows) == 0:
                logging.warning(
                    "No stars with specified names exist in dataset")
                logging.warning("Continuing without star removal")
            else:
                df = df.drop(index=star_rows)
                logging.info("Removed stars: %s", bad_stars)
        except KeyError as e:
            logging.error("Failed to remove specified stars")
            logging.error("Error received: %s", e)
            logging.warning("Continuing without star removal")
    return df


def clean_headers(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    df.columns = (df.columns.str.strip().str.lower().str.replace(
        " ", "_").str.replace("(", "_").str.replace(")", "").str.replace(
            "<", "").str.replace(">", ""))
    # Cleanup of headers, could be made more succinct with a simple REGEX or two

    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this function.
    extracted_column_names = df.columns
    # Finds common column names
    intersection = np.intersect1d(columns, extracted_column_names)
    return df[intersection]
