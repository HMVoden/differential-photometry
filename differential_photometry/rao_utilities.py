import numpy as np
import pandas as pd

import differential_photometry.rao_data as data


def arrange_iterables(row: int, col: int, iterables):
    """Arranges an entire set of lists in accordance with the row column shape specified

    Parameters
    ----------
    row : int
        Number of rows
    col : int
        Number of columns
    iterables : list-like
        A list of lists that will be reshaped

    Returns
    -------
    ndarray
        Numpy array of all the arrays reconfigured in specified shape
    """
    results = []
    for l in iterables:
        l = np.asanyarray(l)  # make sure it's an array
        l = l.reshape(row, col)
        results.append(l)

    return np.array(results)


def arrange_time_star(df: pd.DataFrame, columns: list):
    """Arranges a set of data from a dataframe in a time=row, star=column format

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing columns   
    columns : list
        Column names that are to be reshaped

    Returns
    -------
    dict(str:ndarray)
        a dict of key:values that are column name: arranged numpy array
    """
    stars, samples = data.extract_samples_stars(df)
    num_columns = len(columns)
    # get only the columns we're interested in
    values = df[columns]
    # split columns into their own arrays
    values = np.hsplit(values, num_columns)
    arranged = arrange_iterables(samples, stars, values)
    return dict(zip(columns, arranged))


def arrange_for_dataframe(df: pd.DataFrame, *arrays):
    """Rearranges a list to fit into a dataframe

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe that list will be fit into, needed for length of frame

    Returns
    -------
    ndarray
        Numpy array of all the passed in lists that have been arranged to fit dataframe
    """
    dataframe_length = df.shape[0]
    to_arrange = []
    for a in arrays:
        a = np.asanyarray(a)
        # Easier to pass into arrange function
        to_arrange.append(a.transpose())

    return arrange_iterables(dataframe_length, 1, to_arrange)
