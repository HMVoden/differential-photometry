import logging

import pandas as pd


def clean_stars_data(dataframe: pd.DataFrame) -> pd.DataFrame:
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
        dataframe = dataframe.rename(columns={"obj": "name"})

    required_columns = ["mag", "error", "jd", "name"]
    for col in required_columns:
        if col not in dataframe.columns:
            raise KeyError(
                "Unable to continue program, missing critical column: {0}".
                format(col))

    datatypes = dataframe.dtypes
    if not (datatypes.mag.name
            == "float64"):  # Could make this apply to error and error_t too
        logging.warning(
            "Data column '{0}' is not a numerical type, attempting to fix".
            format("mag"))
        # First instance of bad data
        bad_mags = dataframe[(dataframe.mag == "Flux<0")]

        stars_removed = bad_mags.name.unique()
        star_rows = dataframe[(dataframe["name"].isin(stars_removed))]

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
        Dataframe to be cleaned, must contain "name" column

    Returns
    -------
    pd.DataFrame
        Dataframe cleaned
    """
    row_counts = df["name"].value_counts()
    # most common value
    row_mode = row_counts.mode()[0]
    bad_stars = row_counts[row_counts != row_mode].index.values
    if len(bad_stars) > 0:
        logging.warning(
            "Stars have been found without sufficient amount of information")
        logging.warning("Removing star(s) {0} from dataset".format(*bad_stars))
        star_rows = df[df["name"].isin(bad_stars)]
        df = df.drop(index=star_rows.index)
    return df
