import logging
from typing import List

import differential_photometry.maths.stats as stat
import pandas as pd
from differential_photometry.maths.differential_photometry import (
    calculate_differential_average, calculate_differential_magnitude,
    calculate_differential_uncertainty)
from differential_photometry.utilities.data import (arrange_for_dataframe,
                                                    arrange_time_star)
from differential_photometry.utilities.math import calculate_on_dataset
from differential_photometry.utilities.stats import stat_runner


def find_varying_stars(df: pd.DataFrame,
                       method="adf_gls",
                       p_value=0.05,
                       null="accept",
                       clip=False,
                       data="mag") -> pd.DataFrame:
    """Takes a dataframe containing a numerical data column and applies the specified
    statistical test on it, then compares the resulting p-value to the threshold value.
    Some tests, such as the Dickson-Fuller test, have a null hypothesis that the timeseries in question
    is non-stationary and if we want to know if a star is variable we must set the null to 'accept' that hypothesis.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing numerical timeseries columns and a name column to group by
    method : str, optional
        Statistical test name, by default "chisquared"
    threshold : float, optional
        The p-value threshold on which we want to reject or accept the hypothesis, by default 0.05
    null : str, optional
        Whether we want to accept or reject the hypothesis to know if a star is variable, by default "accept"
    clip : bool, optional
        Whether to sigma clip the data and possibly error for the statistical test, by default False
    data : str, optional
        The data column to operate the varying star detection on, by default "mag"

    Returns
    -------
    pd.DataFrame
        Dataframe containing the statistical test column and a "varying" truth column
    """

    stars = df.groupby("name")
    error_name = None
    if method == "chisquared":
        stat_function = stat.reduced_chi_square
        error_name = "error"
    if method == "adfuller":
        stat_function = stat.augmented_dfuller
    if method == "kpss":
        stat_function = stat.kpss
    if method == "zivot_andrews":
        stat_function = stat.zastat
    if method == "adf_gls":  # best one so far
        stat_function = stat.adf_gls

    test_statistic = stars.apply(
        func=stat_runner,
        data_name=data,
        error_name=error_name,
        clip=clip,
        stat_func=stat_function).rename(method).reset_index()

    # Combine test-statistic column with old dataframe
    df = pd.merge(df, test_statistic, how="left", on="name")
    if null == "accept":
        df["varying"] = df[method] >= p_value
    else:
        df["varying"] = df[method] <= p_value

    return df


def calculate_differential_photometry(df: pd.DataFrame) -> pd.DataFrame:

    required_cols = ["mag", "error"]
    # In case there are no varying stars
    if "varying" in df.columns and not df[df["varying"] == True].empty:
        # Groupby won't work here as we need both sets to do this
        non_varying = df[df["varying"] == False]
        varying = df[df["varying"] == True]
        var_raw = arrange_time_star(varying, required_cols)
        var_mag = var_raw["mag"]
        var_error = var_raw["error"]
    else:
        non_varying = df
        varying = pd.DataFrame()
        var_mag = None
        var_error = None
    ref_raw = arrange_time_star(non_varying, required_cols)
    raw_mag = ref_raw["mag"]
    raw_error = ref_raw["error"]

    subtracted_mags = calculate_difference(magnitudes=raw_mag,
                                           varying_magnitudes=var_mag)

    subtracted_err = calculate_difference_uncertainties(
        errors=raw_error, varying_errors=var_error)

    for index, mag in enumerate(subtracted_mags):
        err = subtracted_err[index]
        averages = calculate_differential_average(subtracted_mags=mag,
                                                  calculated_errors=err)
        # apply function to everything in averages dictionary
        # so we can properly put it into the dataframe

        if index == 0:
            averages = {
                k: arrange_for_dataframe(non_varying, v)[0]
                for k, v in averages.items()
            }
            non_varying = non_varying.assign(**averages)
        else:
            averages = {
                k: arrange_for_dataframe(varying, v)[0]
                for k, v in averages.items()
            }
            varying = varying.assign(**averages)

    return pd.concat([non_varying, varying], join="outer")


def find_varying_diff_calc(df: pd.DataFrame,
                           method: str = "chisquared",
                           p_value: int = 4,
                           null="accept",
                           clip=False,
                           iterations=1) -> pd.DataFrame:
    day = df["d_m_y"].unique()
    logging.info("Processing day %s", day)
    for i in range(0, iterations, 1):
        # Step 1, get average differential
        df = calculate_differential_photometry(df)
        # Step 2, remove varying and method columns for recalculation
        df = df.drop(columns=["varying", method], errors='ignore')
        # Step 3, find varying stars via average differential
        df = find_varying_stars(df, method, p_value, null, clip,
                                "average_diff_mags")
        logging.info("Iteration %s found %s varying stars", i + 1,
                     df[df["varying"] == True]["name"].nunique())
    return df


def calculate_difference(magnitudes: List[float],
                         varying_magnitudes: List[float] = None) -> List[List]:

    calc_results = calculate_on_dataset(targets=magnitudes,
                                        func=calculate_differential_magnitude,
                                        excluded_targets=varying_magnitudes)
    return calc_results


def calculate_difference_uncertainties(errors: List[float],
                                       varying_errors: List[float] = None
                                       ) -> List[List]:

    calc_results = calculate_on_dataset(
        targets=errors,
        func=calculate_differential_uncertainty,
        excluded_targets=varying_errors)

    return calc_results
