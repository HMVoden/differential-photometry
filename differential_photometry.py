# %%
import warnings
import logging
from pathlib import PurePath

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import importlib

from feets import ExtractorWarning

import rao_analysis as analysis
import rao_math as m
import rao_models as model
import rao_plotting as plot
import rao_stats as stat
import rao_utilities as util
import rao_data as data
import rao_differential_photometry as diff

importlib.reload(m)
importlib.reload(util)
importlib.reload(analysis)
importlib.reload(data)
importlib.reload(diff)
importlib.reload(plot)


# CONSTANTS ============================================================================
# FILENAME = 'data/data.csv'
FILENAME = 'data/M3_raw01_Photometry25-47-59.csv'
# FILENAME = 'data/M3_raw02_Photometry25-47-59.csv'
# FILENAME = 'data/M3_raw03_Photometry28-47-55.csv'
# FILENAME = 'data/M3_raw04_Photometry35-47-55.csv'
# FILENAME = 'data/M3_raw01_Photometry28_47_55_may_29.csv'
# FILENAME = 'data/M3_2nights_rawPhotometry.csv'
# FILENAME = 'data/M3_night_1.xlsx'
# FILENAME = 'data/M3_night_2.xlsx'
EXPOSURE_TIME = 2.5

warnings.simplefilter(action='ignore', category=FutureWarning)
# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ExtractorWarning)
# FUNCTIONS ============================================================================

# I moved everything into different python modules since this was getting extremely large

# CALCULATION ============================================================================
logging.basicConfig()
logging.getLogger().setLevel(logging.WARNING)
file = PurePath(FILENAME)

df = data.extract(FILENAME)
bad_rows = df[df['name'] == 'M3-12']
# TODO write code that cleans insufficient datasets like M3-12 here
df = df.drop(index=bad_rows.index)

num_stars, num_samples = data.extract_samples_stars(df)

if 'jd' in df.columns:
    timeline = df['jd'].unique()
    df['time'] = pd.to_datetime(df['jd'], origin='julian', unit='D')
else:
    timeline = np.linspace(0, num_samples*EXPOSURE_TIME, num_samples)

# Step 1, find obvious varying stars
non_varying, varying = analysis.find_varying_stars(df)

df = diff.calculate_differential_photometry(non_varying, varying)

non_varying = df[df['varying'] == False]
varying = df[df['varying'] == True]

# varying.to_excel('test.xlsx')

# degree = 8
# Step 2, find trend in non-varying stars
trend = analysis.find_biweight_trend(non_varying)

# Step 3, remove trend from non-varying stars
# if not analysis.is_trend_constant(trend):
#     detrended = analysis.detrend_dataset(non_varying, trend)

#     # Step 4, verify all non-varying stars are non-varying

#     detrended_varying, detrended_non_varying = analysis.find_varying_stars(
#         detrended)

#     plot.plot_and_save_all_4_grid(
#         detrended_non_varying, ("detrended_non_varying_" + file.stem))
#     plot.plot_and_save_all_4_grid(
#         detrended_varying, ("detrended_varying_" + file.stem))
plot.plot_and_save_all_4_grid(varying, ("varying/varying_" + file.stem))
plot.plot_and_save_all_4_grid(
    non_varying, ("non_varying/non_varying_" + file.stem))
# plot.plot_and_save_all_4_grid(df, file.stem)

# %%
