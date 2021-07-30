from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

import logging


def extract_samples_stars(dataframe: pd.DataFrame) -> Tuple[int, int]:
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
    if dataframe.empty:
        return (0, 0)
    rows = dataframe.shape[0]
    num_stars = dataframe["id"].nunique()
    samples = int(rows / num_stars)
    return samples, num_stars


def split_on(df: pd.DataFrame, split_on: str):
    """Splits dataframe on a boolean

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to be split
    split_on : str
        Column name of a boolean dataframe column

    Returns
    -------
    pd.Dataframe, pd.Dataframe
        Dataframes that have been split on the column name specified, ordered by
        negative, positive (false, true)
    """
    false_df = df[df[split_on] == False]
    true_df = df[df[split_on] == True]
    return false_df, true_df


def split_varying(df: pd.DataFrame):
    inter_varying = df[df.inter_varying == True]  # Varying
    intra_varying = df[
        (df.inter_varying == False) & (df.graph_intra == True)
    ]  # Briefly varying
    non_varying = df[(df.inter_varying == False) & (df.graph_intra == False)]

    return non_varying, intra_varying, inter_varying


# def flag_variable(df: pd.DataFrame) -> pd.DataFrame:
#     """Goes through each star and if any star has any day flagged as
#     variable, this flags every day as variable. For use before plotting

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Dataframe to flag

#     Returns
#     -------
#     pd.DataFrame
#         Flagged dataframe
#     """

#     df["graph_intra"] = df.groupby("id")["intra_varying"].transform(pd.DataFrame.any)
#     df["varying"] = df["graph_intra"] | df["inter_varying"]

#     return df


def arrange_for_dataframe(*arrays):
    """Finds the length of a dataframe and then changes each iterable passed
    into the function into the same length to be added into the dataframe

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to extract length from

    Returns
    -------
    np.ndarray
        Numpy array of all the iterables that have been rearranged
    """
    for a in arrays:
        a = np.asanyarray(a)  # safety check
        yield a.ravel()


def arrange_time_star(time: int, stars: int, *arrays):
    """Finds out how many samples and stars are in a given dataframe
    then rearranges the columns in a way that each time increases on columns
    and stars change on each row

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing data columns
    columns : list
        Names of each datacolumn to be arranged

    Returns
    -------
    np.ndarray
        Numpy array of rearranged data columns
    """

    return arrange_iterables(time, stars, *arrays)


def arrange_iterables(row: int, col: int, *iterables):
    """Generic function to reshape numpy arrays in the specified row/column arrangements, if possible

    Parameters
    ----------
    row : int
        Number of rows desired
    col : int
        Number of columns desired
    iterables : List
        iterables to turn into numpy arrays and reshape

    Returns
    -------
    np.ndarray
        Numpy array of all the iterables that have been reshaped
    """
    for l in iterables:
        l = np.asanyarray(l)  # make sure it's an array
        l = l.reshape(row, col)
        yield l


def flatten_dictionary(dictionary: Dict) -> Dict:
    """Flattens a nested dictionary. Taken from https://stackoverflow.com/a/48700937

    Parameters
    ----------
    dictionary : Dict
        Dictionary to flatten

    Returns
    -------
    Dict
        Flattened dictionary
    """
    result = {}

    for d in dictionary:
        temp = {}
        for key in d:
            temp.update(d[key])

        result.update(**temp)
    return


def group_by_year_month_day(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby([df["time"].dt.year, df["time"].dt.month, df["time"].dt.day])


def group_by_day_month_year(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby([df["time"].dt.day, df["time"].dt.month, df["time"].dt.year])


def time_from_data(jd: List[float]) -> pd.DatetimeTZDtype:
    time = pd.to_datetime(jd, origin="julian", unit="D")
    unique_years = time.year.nunique()
    unique_months = time.month.nunique()
    unique_days = time.day.nunique()

    logging.info("Number of days found in dataset: %s", unique_days)
    logging.info("Number of months found in dataset: %s", unique_months)
    logging.info("Number of years found in dataset: %s", unique_years)

    return time
