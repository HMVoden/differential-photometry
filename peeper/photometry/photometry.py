import gc
import logging
from typing import List

import config.manager as config
import peeper.data.utilities as data_utils
import peeper.photometry.math as p_math
import peeper.progress_bars as bars
import peeper.stats.stats as stats
import numpy as np
import pandas as pd


def calculate_differential_photometry(
    df: pd.DataFrame, varying_flag: str
) -> pd.DataFrame:
    non_varying = df[df[varying_flag] == False]
    non_varying_shape = data_utils.extract_samples_stars(non_varying)
    varying = df[df[varying_flag] == True]
    varying_shape = data_utils.extract_samples_stars(varying)

    non_var_mag = non_varying["mag"].to_numpy().reshape(non_varying_shape).transpose()
    var_mag = varying["mag"].to_numpy().reshape(varying_shape).transpose()

    non_var_error = (
        non_varying["error"].to_numpy().reshape(non_varying_shape).transpose()
    )
    var_error = varying["mag"].to_numpy().reshape(varying_shape).transpose()

    var_diff_result = []
    var_err_result = []
    for index, star in enumerate(var_mag):
        sub_mag = p_math.calculate_differential_magnitude(star, non_var_mag).transpose()
        sub_error = p_math.calculate_differential_uncertainty(
            var_error[index], non_var_error
        ).transpose()
        var_avg_diff, var_avg_err = p_math.calculate_differential_average(
            subtracted_mags=sub_mag, calculated_errors=sub_error
        )
        var_diff_result.append(var_avg_diff)
        var_err_result.append(var_avg_err)

    if not varying.empty:
        var_diff_result = np.asarray(var_diff_result)
        var_err_result = np.asarray(var_err_result)

        varying["average_diff_mags"] = var_diff_result.ravel("F")
        varying["average_uncertainties"] = var_err_result.ravel("F")
        del var_diff_result
        del var_err_result
        gc.collect()

    diff_result = []
    err_result = []
    for index, star in enumerate(non_var_mag):
        sub_mag = p_math.calculate_differential_magnitude(
            star, np.delete(non_var_mag, index, axis=0)
        ).transpose()
        sub_error = p_math.calculate_differential_uncertainty(
            non_var_error[index], np.delete(non_var_error, index, axis=0)
        ).transpose()
        avg_diff, avg_err = p_math.calculate_differential_average(
            subtracted_mags=sub_mag, calculated_errors=sub_error
        )
        diff_result.append(avg_diff)
        err_result.append(avg_err)
    diff_result = np.asarray(diff_result)
    err_result = np.asarray(err_result)
    non_varying["average_diff_mags"] = diff_result.ravel("F")
    non_varying["average_uncertainties"] = err_result.ravel("F")
    del diff_result
    del err_result
    gc.collect()

    return pd.concat([non_varying, varying], join="outer")


def iterate_differential_photometry(
    df: pd.DataFrame,
    method: str = "chisquared",
    p_value: int = 4,
    null="accept",
    clip=False,
    iterations=1,
    pbar_method=None,
    varying_flag="varying",
) -> pd.DataFrame:
    logging.info("Processing day %s", df.name)
    pbar_iter = bars.get_progress_bar(
        "iterations",
        total=iterations,
        desc="    Variable star detection iterations",
        unit="iteration",
        leave=False,
        color="cyan",
    )
    for i in range(0, iterations, 1):
        # Step 1, get average differential
        df = calculate_differential_photometry(df=df, varying_flag=varying_flag)
        gc.collect()
        # Step 2, remove varying and method columns for recalculation
        # ignore errors if columns aren't present
        # Step 3, find varying stars via average differential
        df[method] = df.groupby("id")["average_diff_mags"].transform(
            stats.test_stationarity, method=method, clip=clip
        )
        if null == "accept":
            df[varying_flag] = df[method] >= p_value
        else:
            df[varying_flag] = df[method] <= p_value

        logging.info(
            "Iteration %s found %s varying stars",
            i + 1,
            df[df[varying_flag] == True]["id"].nunique(),
        )
        pbar_iter.update()
    if pbar_method is not None:
        pbar_method()
    gc.collect()
    return df


def intra_day_iter(df: pd.DataFrame) -> pd.DataFrame:
    app_config = config.get("application")
    iterations = config.get("iterations")
    status = bars.status
    status.update(demo="Calculating photometry and finding variable stars")
    star_detection_method = app_config["star_detection"]["method"]
    # Group by year/month/day to prevent later months from being
    # before earlier months, with an earlier day.
    # e.g. 1/7/2021 being before 22/6/2021
    status.update(demo="Differential Photometry per day")
    intra_pbar = bars.get_progress_bar(
        name="intra_diff",
        total=df["y_m_d"].nunique(),
        desc="  Calculating and finding variable intra-day stars",
        unit="Days",
        color="blue",
        leave=False,
    )
    logging.info("Detecting intra-day variable stars...")
    varying_flag = "intra_varying"
    df[varying_flag] = False
    # Drop=True to prevent index error with Pandas
    return (
        df.groupby("y_m_d")
        .apply(
            iterate_differential_photometry,
            method=star_detection_method,
            pbar_method=intra_pbar.update,
            iterations=iterations,
            **app_config[star_detection_method],
            varying_flag=varying_flag
        )
        .reset_index(drop=True)
    )


def inter_day(df: pd.DataFrame) -> pd.DataFrame:
    app_config = config.get("application")
    star_detection_method = app_config["star_detection"]["method"]
    status = bars.status
    status.update(demo="Differential Photometry per star")

    # TODO Throw in callback function for inter_pbars
    inter_pbar = bars.get_progress_bar(
        name="inter_diff",
        total=df.id.nunique(),
        desc="  Calculating and finding variable inter-day stars",
        unit="Days",
        color="blue",
        leave=False,
    )
    # Detecting if stars are varying across entire dataset
    logging.info("Detecting inter-day variable stars...")

    df[star_detection_method] = (
        df.groupby("id")["c_average_diff_mags"]
        .transform(
            stats.test_stationarity,
            method=star_detection_method,
            clip=app_config[star_detection_method]["clip"],
        )
        .reset_index(drop=True)
    )
    inter_pbar.update(df.id.nunique())
    p_value = app_config[star_detection_method]["p_value"]
    null = app_config[star_detection_method]["null"]
    if null == "accept":
        df["inter_varying"] = df[star_detection_method] >= p_value
    else:
        df["inter_varying"] = df[star_detection_method] <= p_value
    return df


def calculate_difference(
    non_varying: pd.DataFrame, varying: pd.DataFrame
) -> List[List]:
    return p_math.calculate_on_dataset(
        targets=non_varying,
        func=p_math.calculate_differential_magnitude,
        excluded=varying,
    )


def calculate_difference_uncertainties(
    non_varying: pd.DataFrame, varying: pd.DataFrame
) -> List[List]:
    return p_math.calculate_on_dataset(
        targets=non_varying,
        func=p_math.calculate_differential_uncertainty,
        excluded=varying,
    )
