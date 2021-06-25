# %%
import importlib
import logging
import warnings
import time
from pathlib import PurePath

import pandas as pd
from feets import ExtractorWarning

import rao_analysis as analysis
import rao_data as data
import rao_differential_photometry as diff
import rao_math as m
import rao_models as model
import rao_plotting as plot
import rao_stats as stat
import rao_utilities as util

importlib.reload(m)
importlib.reload(util)
importlib.reload(analysis)
importlib.reload(data)
importlib.reload(diff)
importlib.reload(plot)


# CONSTANTS ============================================================================
# FILENAME = 'data/data.csv'
# FILENAME = 'data/M3_raw01_Photometry25-47-59.csv'
# FILENAME = 'data/M3_2nights_rawPhotometry.csv'
# FILENAME = 'data/M3_night_1.xlsx'
# FILENAME = 'data/M3_night_2.xlsx'
FILENAME = 'data/M92_rawPhotometry_v01_total.csv'
start_time = time.time()

# Need this to prevent it from spamming
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# CALCULATION ============================================================================
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
file = PurePath(FILENAME)
dataset = file.stem.split("_")[0]

df = data.extract(FILENAME)

df = data.remove_incomplete_sets(df)

day_dataframes = data.split_on_new_days(df)

processed_frames = []
for name, frame in day_dataframes:
    #     # Step 1, find obvious varying stars
    logging.info("Processing dataframe for day %s", name)
    non_varying, varying = analysis.find_varying_stars(frame)

    frame = diff.calculate_differential_photometry(non_varying, varying)
    processed_frames.append(frame)

# # Step 2, find trend in non-varying stars
# trend = analysis.find_biweight_trend(non_varying)

# # Step 3, remove trend from non-varying stars
# # if not analysis.is_trend_constant(trend):
# detrended = analysis.detrend_dataset(non_varying, trend)

# # Step 4, verify all non-varying stars are non-varying

# detrended_non_varying, detrended_varying = analysis.find_varying_stars(
#     detrended)

df = pd.concat(processed_frames, join="outer")

# Plotting
# plot.plot_and_save_all(
#     detrended_non_varying, ("detrended/detrended_non_varying_" + file.stem))
# plot.plot_and_save_all(
#     detrended_varying, ("detrended/detrended_varying_" + file.stem))
# plot.plot_and_save_all(varying, ("varying/varying_" + file.stem))
# plot.plot_and_save_all(
#     non_varying, ("non_varying/non_varying_" + file.stem))
# plot.plot_and_save_all(df=df,
#                        uniform_y_axis=False,
#                        folder="output",
#                        dataset=dataset,
#                        filename=file.stem
#                        )
logging.info("Program executed in: %s seconds", (time.time() - start_time))
