import logging
from pathlib import PurePath

import numpy as np
import pandas as pd


def extract(filename: str) -> pd.DataFrame:
    """ Assuming there are headers in the data file, this takes the filename opens it and reads it
    into a pandas dataframe, cleans the headers to make it all lowercase with no parenthesis and returns only
    the columns we're interested in.

    Parameters
    ----------
    filename : str
        Filename of datafile

    Returns
    -------
    pd.DataFrame
        Dataframe containing only required columns, trimmed and made usable
    """

    data_path = PurePath(filename)
    if (
        data_path.suffix == ".xlsx"
    ):  # This way we can ignore if it's a csv or excel file
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "_")
        .str.replace(")", "")
        .str.replace("<", "")
        .str.replace(">", "")
    )
    # Cleanup of headers, could be made more succinct with a simple REGEX
    desired_column_names = np.array(["obj", "name", "mag", "error", "x", "y", "jd"])
    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this script.
    extracted_column_names = df.columns
    # Finds common column names
    intersection = np.intersect1d(desired_column_names, extracted_column_names)
    df = clean_stars_data(df[intersection])
    # names index for future use
    df.index.name = "index"
    if "jd" in df.columns:
        df["time"] = pd.to_datetime(df["jd"], origin="julian", unit="D")
        unique_years = df["time"].dt.year.unique()
        unique_months = df["time"].dt.month.unique()
        unique_days = df["time"].dt.day.unique()
        df["d_m_y"] = df["time"].dt.strftime("%d-%m-%Y")

        logging.info("Number of days found in dataset: %s", len(unique_days))
        logging.info("Number of months found in dataset: %s", len(unique_months))
        logging.info("Number of years found in dataset: %s", len(unique_years))
    return df


def extract_samples_stars(dataframe: pd.DataFrame) -> int:
    """Determines and returns the number of different star samples and number of stars as integers

    Parameters
    ----------
    dataframe : pd.DataFrame
        dataframe containing all stars with a unique name

    Returns
    -------
    int, int
        number of stars, number of samples of those stars
    """
    rows = dataframe.shape[0]
    num_stars = dataframe["name"].nunique()
    samples = int(rows / num_stars)
    return num_stars, samples


def clean_stars_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Ensures that the columns mag, error, error_t and either obj or name are present.
    Then makes sure that the mag, error and error_t are viable and in the right format.
    Removes all stars with any mag value of "Flux<0"

    Keyword Arguments:
    dataframe -- A pandas dataframe containing the proper column names
    """
    if "obj" in dataframe.columns:
        dataframe = dataframe.rename(columns={"obj": "name"})

    required_columns = ["mag", "error"]
    for col in required_columns:
        if col not in dataframe.columns:
            raise KeyError(
                "Unable to continue program, missing critical column: {0}".format(col)
            )
    if "name" not in dataframe.columns and "obj" not in dataframe.columns:
        raise KeyError(
            """Unable to continue program, 
                    missing name/object columns for number of star
                    calculations"""
        )

    datatypes = dataframe.dtypes
    if not (
        datatypes.mag.name == "float64"
    ):  # Could make this apply to error and error_t too
        logging.warning(
            "Data column '{0}' is not a numerical type, attempting to fix".format("mag")
        )
        # First instance of bad data
        bad_mags = dataframe[(dataframe.mag == "Flux<0")]

        stars_removed = bad_mags.name.unique()
        star_rows = dataframe[(dataframe["name"].isin(stars_removed))]

        logging.warning("Removing star(s) {0} from dataset".format(stars_removed))
        dataframe = dataframe.drop(index=star_rows.index)
        dataframe["mag"] = pd.to_numeric(dataframe["mag"])

    return dataframe


def remove_incomplete_sets(df):
    row_counts = df["name"].value_counts()
    # most common value
    row_mode = row_counts.mode()[0]
    bad_stars = row_counts[row_counts != row_mode].index.values
    if len(bad_stars) > 0:
        logging.warning(
            "Stars have been found without sufficient amount of information"
        )
        logging.warning("Removing star(s) {0} from dataset".format(*bad_stars))
        star_rows = df[df["name"].isin(bad_stars)]
        df = df.drop(index=star_rows.index)
    return df
