import logging
from typing import List

import pandas as pd

import differential_photometry.photometry.math as p_math
import differential_photometry.stats.stats as stats
import differential_photometry.data.utilities as data
import differential_photometry.progress_bars as bars
import differential_photometry.timeseries.timeseries as ts

import config.manager as config


def calculate_differential_photometry(df: pd.DataFrame,
                                      varying_flag="varying") -> pd.DataFrame:

    required_cols = ["mag", "error"]
    # In case there are no varying stars
    if varying_flag in df.columns and not df[df[varying_flag] == True].empty:
        # Groupby won't work here as we need both sets to do this
        non_varying, varying = data.split_on(df, varying_flag)
        var_raw = data.arrange_time_star(varying, required_cols)
        var_mag = var_raw["mag"]
        var_error = var_raw["error"]
    else:
        non_varying = df
        varying = pd.DataFrame()
        var_mag = None
        var_error = None
    ref_raw = data.arrange_time_star(non_varying, required_cols)
    raw_mag = ref_raw["mag"]
    raw_error = ref_raw["error"]

    subtracted_mags = calculate_difference(magnitudes=raw_mag,
                                           varying_magnitudes=var_mag)

    subtracted_err = calculate_difference_uncertainties(
        errors=raw_error, varying_errors=var_error)

    for index, mag in enumerate(subtracted_mags):
        err = subtracted_err[index]
        averages = p_math.calculate_differential_average(subtracted_mags=mag,
                                                         calculated_errors=err)
        # apply function to everything in averages dictionary
        # so we can properly put it into the dataframe

        if index == 0:
            averages = {
                k: data.arrange_for_dataframe(non_varying, v)[0]
                for k, v in averages.items()
            }
            non_varying = non_varying.assign(**averages)
        else:
            averages = {
                k: data.arrange_for_dataframe(varying, v)[0]
                for k, v in averages.items()
            }
            varying = varying.assign(**averages)

    return pd.concat([non_varying, varying], join="outer")


def iterate_differential_photometry(df: pd.DataFrame,
                                    method: str = "chisquared",
                                    p_value: int = 4,
                                    null="accept",
                                    clip=False,
                                    iterations=1,
                                    pbar_method=None,
                                    varying_flag="varying",
                                    detection_data="mag") -> pd.DataFrame:
    logging.info("Processing day %s", df.name)
    result_cols = [varying_flag, method]
    pbar_iter = bars.get_progress_bar(
        "iterations",
        total=iterations,
        desc="    Variable star detection iterations",
        unit="iteration",
        leave=False,
        color="cyan")
    for i in range(0, iterations, 1):
        # Step 1, get average differential
        df = calculate_differential_photometry(df, varying_flag)
        # Step 2, remove varying and method columns for recalculation
        # ignore errors if columns aren't present
        df = df.drop(columns=result_cols, errors='ignore')
        # Step 3, find varying stars via average differential
        df[method] = df.groupby("id")[detection_data].transform(
            stats.test_stationarity, method=method, clip=clip)
        if null == "accept":
            df[(varying_flag)] = df[method] >= p_value
        else:
            df[varying_flag] = df[method] <= p_value

        logging.info("Iteration %s found %s varying stars", i + 1,
                     df[df[varying_flag] == True]["id"].nunique())
        pbar_iter.update()
    if pbar_method is not None:
        pbar_method()
    return df


def intra_day_iter(df: pd.DataFrame) -> pd.DataFrame:

    app_config = config.get("application")
    iterations = config.get("iterations")
    status = bars.status
    star_detection_method = app_config["star_detection"]["method"]
    # Group by year/month/day to prevent later months from being
    # before earlier months, with an earlier day.
    # e.g. 1/7/2021 being before 22/6/2021
    days = data.group_by_year_month_day(df)
    status.update(demo="Differential Photometry per day")
    intra_pbar = bars.get_progress_bar(
        name="intra_diff",
        total=len(days),
        desc="  Calculating and finding variable intra-day stars",
        unit="Days",
        color="blue",
        leave=False)
    logging.info("Detecting intra-day variable stars...")
    # Drop=True to prevent index error with Pandas
    df = days.apply(iterate_differential_photometry,
                    method=star_detection_method,
                    pbar_method=intra_pbar.update,
                    iterations=iterations,
                    **app_config[star_detection_method],
                    varying_flag="intra_varying",
                    detection_data="average_diff_mags").reset_index(drop=True)
    return df


def inter_day(df: pd.DataFrame) -> pd.DataFrame:
    app_config = config.get("application")
    star_detection_method = app_config["star_detection"]["method"]
    status = bars.status
    status.update(demo="Differential Photometry per star")
    df = ts.correct_offset(df)
    stars = df.groupby("id")
    # TODO Throw in callback function for inter_pbars
    inter_pbar = bars.get_progress_bar(
        name="inter_diff",
        total=len(stars),
        desc="  Calculating and finding variable inter-day stars",
        unit="Days",
        color="blue",
        leave=False)
    # Detecting if stars are varying across entire dataset
    logging.info("Detecting inter-day variable stars...")

    df[star_detection_method] = stars["c_average_diff_mags"].transform(
        stats.test_stationarity,
        method=star_detection_method,
        clip=app_config[star_detection_method]["clip"]).reset_index(drop=True)
    inter_pbar.update(len(stars))
    p_value = app_config[star_detection_method]["p_value"]
    null = app_config[star_detection_method]["null"]
    if null == "accept":
        df["inter_varying"] = df[star_detection_method] >= p_value
    else:
        df["inter_varying"] = df[star_detection_method] <= p_value
    return df


def calculate_difference(magnitudes: List[float],
                         varying_magnitudes: List[float] = None) -> List[List]:

    calc_results = p_math.calculate_on_dataset(
        targets=magnitudes,
        func=p_math.calculate_differential_magnitude,
        excluded_targets=varying_magnitudes)
    return calc_results


def calculate_difference_uncertainties(errors: List[float],
                                       varying_errors: List[float] = None
                                       ) -> List[List]:

    calc_results = p_math.calculate_on_dataset(
        targets=errors,
        func=p_math.calculate_differential_uncertainty,
        excluded_targets=varying_errors)

    return calc_results
