from typing import Dict, List

import numpy as np
import pandas as pd

from astropy.stats import sigma_clip


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
    num_stars = dataframe["id"].nunique()
    samples = int(rows / num_stars)
    return num_stars, samples


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
    inter_varying = df[df.inter_varying == True]
    intra_varying = df[(df.inter_varying == False) & (df.graph_intra == True)]
    non_varying = df[(df.inter_varying == False) & (df.graph_intra == False)]

    return non_varying, intra_varying, inter_varying


def flag_intra_variable(df: pd.DataFrame) -> pd.DataFrame:
    """Goes through each star and if any star has any day flagged as
    variable, this flags every day as variable. For use before plotting

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to flag

    Returns
    -------
    pd.DataFrame
        Flagged dataframe
    """

    df["graph_intra"] = df.groupby("id")["intra_varying"].transform(
        pd.DataFrame.any)

    return df


def arrange_for_dataframe(df: pd.DataFrame, *arrays):
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
    # TODO make into dictionary to return
    dataframe_length = df.shape[0]
    to_arrange = []
    for a in arrays:
        a = np.asanyarray(a)
        # Easier to pass into arrange function
        to_arrange.append(a.transpose())

    return arrange_iterables(dataframe_length, 1, to_arrange)


def arrange_time_star(df: pd.DataFrame, columns: list):
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
    stars, samples = extract_samples_stars(df)
    num_columns = len(columns)
    # get only the columns we're interested in
    values = df[columns]
    # split columns into their own arrays
    values = np.hsplit(values, num_columns)
    arranged = arrange_iterables(samples, stars, values)
    return dict(zip(columns, arranged))


def arrange_iterables(row: int, col: int, iterables):
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
    results = []
    for l in iterables:
        l = np.asanyarray(l)  # make sure it's an array
        l = l.reshape(row, col)
        results.append(l)

    return np.array(results)


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
    return df.groupby(
        [df["time"].dt.year, df["time"].dt.month, df["time"].dt.day])


def get_largest_range(**data: Dict):
    """Finds the largest range in one part of a timeseries dataset, for example
    if you have three days of timeseries, this will find the largest range that
    can be found in a single day

    Returns
    -------
    Dict
        Dictionary of the data name passed in and the entire dataset of values as the
        dictionary value.

    Returns
    -------
    Dict
        Dictionary of the data name and the largest range for the entire dataset
    """
    result = []
    for d in data.values():
        d = np.abs(sigma_clip(d, sigma=2, axis=1, masked=False))
        max_variation = np.nanmax(
            np.abs((np.nanmax(d, axis=1) - np.nanmin(d, axis=1))))
        result.append(max_variation)
    return dict(zip(data.keys(), result))
