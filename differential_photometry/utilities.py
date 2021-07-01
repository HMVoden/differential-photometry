import logging

import numpy as np
import pandas as pd

import differential_photometry.analysis as analysis
import differential_photometry.data as data
import differential_photometry.differential_photometry as diff


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


def correct_offset(df: pd.DataFrame) -> pd.DataFrame:

    non_varying = df[df["varying"] == False]
    # Probably close to what it 'really' is across all days,
    # more data points will make it closer to real mean.
    true_mean = non_varying.groupby("name").agg({
        "mag": "mean",
        "average_diff_mags": "mean"
    })
    # Individual day means to find offset
    day_star_mean = non_varying.groupby(["d_m_y", "name"]).agg({
        "mag":
        "mean",
        "average_diff_mags":
        "mean"
    })
    offset = day_star_mean.sub(true_mean, axis="index").reset_index()
    # Median of offsets to prevent huge outliers from mucking with data
    per_day_offset = offset.groupby("d_m_y").mean().reset_index()
    # rename so merge doesn't go wonky
    per_day_offset = per_day_offset.rename(
        columns={
            "mag": "mag_offset",
            "average_diff_mags": "diff_mag_offset"
        })
    df_corrected = df.copy()
    df_corrected = df_corrected.merge(per_day_offset,
                                      left_on="d_m_y",
                                      right_on="d_m_y",
                                      how="inner")
    df_corrected["mag"] = df_corrected["mag"] - df_corrected["mag_offset"]
    df_corrected["average_diff_mags"] = df_corrected[
        "average_diff_mags"] - df_corrected["diff_mag_offset"]
    df_corrected["corrected"] = True

    return df_corrected


def flag_variable(df: pd.DataFrame) -> pd.DataFrame:
    stars = df.groupby("name")
    updated_frames = []
    for name, star_frame in stars:
        if star_frame["varying"].any():
            star_frame = star_frame.assign(varying=True)
        updated_frames.append(star_frame)

    return pd.concat(updated_frames, join="outer")


def find_varying_diff_calc(df: pd.DataFrame,
                           method: str = "chisquared",
                           threshold: int = 4) -> pd.DataFrame:
    day = df["d_m_y"].unique()
    logging.info("Processing day %s", day)
    df = analysis.find_varying_stars(df, method, threshold)
    return diff.calculate_differential_photometry(df)


def split_on(df: pd.DataFrame, split_on: str):
    false_df = df[df[split_on] == False]
    true_df = df[df[split_on] == True]
    return false_df, true_df
