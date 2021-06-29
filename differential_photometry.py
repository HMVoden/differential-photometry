# %%
import importlib
import logging
import time
import warnings
from pathlib import PurePath

import pandas as pd
from feets import ExtractorWarning

import differential_photometry.rao_analysis as analysis
import differential_photometry.rao_data as data
import differential_photometry.rao_differential_photometry as diff
import differential_photometry.rao_math as m
import differential_photometry.rao_models as model
import differential_photometry.rao_plotting as plot
import differential_photometry.rao_stats as stat
import differential_photometry.rao_utilities as util

importlib.reload(m)
importlib.reload(util)
importlib.reload(analysis)
importlib.reload(data)
importlib.reload(diff)
importlib.reload(plot)
importlib.reload(model)
importlib.reload(stat)


# CONSTANTS ============================================================================
# FILENAME = 'data/data.csv'
# FILENAME = "data/M3_raw01_Photometry25-47-59.csv"
FILENAME = "data/M3_2nights_rawPhotometry.csv"
# FILENAME = 'data/M3_night_1.xlsx'
# FILENAME = 'data/M3_night_2.xlsx'
# FILENAME = "data/M92_rawPhotometry_v01_total.csv"
# FILENAME = 'data/M92_rawPhotometry_v02_total.csv'


# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# CALCULATION ============================================================================

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    file = PurePath(FILENAME)
    dataset = file.stem.split("_")[0]

    df = data.extract(FILENAME)

    df = data.remove_incomplete_sets(df)

    days = df.groupby("d_m_y")

    processed_frames = []
    # Step 1, find obviously varying stars
    # perform differential photometry on them
    for name, frame in days:
        logging.info("Processing dataframe for day %s", name)
        non_varying, varying = analysis.find_varying_stars(frame, threshold=5)

        frame = diff.calculate_differential_photometry(df=non_varying, varying=varying)

        logging.info(
            "Total varying stars in day %s: %s",
            name,
            frame[frame["varying"] == True]["name"].nunique(),
        )

        processed_frames.append(frame)

    df = pd.concat(processed_frames, join="outer")
    # Correct for any offset found in the data
    non_varying = df[df["varying"] == False]

    true_median = non_varying.groupby("name").agg(
        {"mag": "median", "average_diff_mags": "median"}
    )
    day_star_median = non_varying.groupby(["d_m_y", "name"]).agg(
        {"mag": "median", "average_diff_mags": "median"}
    )

    offset = day_star_median.rsub(true_median, axis="index").reset_index()
    cols = ["mag", "average_diff_mags"]
    df_corrected = df.copy()
    df_corrected[cols] = df_corrected[cols] - offset[cols]
    # Set all sets of varying stars, so that we can properly graph them
    stars = df.groupby("name")

    for name, star_frame in stars:
        if star_frame["varying"].any():
            star_frame = star_frame.assign(varying=True)
            df.update(star_frame)

    varying = df[df["varying"] == True]
    non_varying = df[df["varying"] == False]
    # # # Plotting
    # # # plot.plot_and_save_all(
    # # #     detrended_non_varying, ("detrended/detrended_non_varying_" + file.stem))
    # # # plot.plot_and_save_all(
    # # #     detrended_varying, ("detrended/detrended_varying_" + file.stem))
    # # # plot.plot_and_save_all(varying, ("varying/varying_" + file.stem))
    # # # plot.plot_and_save_all(
    # # #     non_varying, ("non_varying/non_varying_" + file.stem))
    plot.plot_and_save_all(
        varying,
        *["output", "corrected", dataset, file.stem, "varying"],
        uniform_y_axis=False,
    )
    plot.plot_and_save_all(
        non_varying,
        *["output", "corrected", dataset, file.stem, "non-varying"],
        uniform_y_axis=False,
    )
