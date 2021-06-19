# %%
import warnings
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

importlib.reload(m)


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
file = PurePath(FILENAME)

df = util.extract_data(FILENAME)
bad_rows = df[df['name'] == 'M3-12']
# TODO write code that cleans insufficient datasets like M3-12 here
df = df.drop(index=bad_rows.index)

num_stars, num_samples = util.extract_samples_stars(df)

if 'jd' in df.columns:
    timeline = df['jd'].unique()
    df['jd'] = pd.to_datetime(df['jd'], origin='julian', unit='D')
else:
    timeline = np.linspace(0, num_samples*EXPOSURE_TIME, num_samples)

adm, au = m.calculate_differential_photometry(magnitudes=df['mag'],
                                              error=df['error'],
                                              num_stars=num_stars,
                                              num_samples=num_samples)

df['average_diff_mags'] = adm
df['average_uncertainties'] = au

# box_model_results = model.box_least_squares(average_diff_mags, average_uncertainties, timeline=timeline)

# # Data export for Dr. Langill
# indices_of_stars = [ sub['name'] for sub in box_model_results]
# original_data_filtered = df.iloc[indices_of_stars]
# original_data_filtered.to_excel('Stars_with_varying_light.xlsx')

# Step 1, find obvious varying stars
varying, non_varying = analysis.find_varying_stars(df)

df = m.calculate_varying(non_varying, varying)

# df = m.calculate_varying(non_varying, varying)
# varying.to_excel('test.xlsx')

# degree = 8
# # Step 2, find trend in non-varying stars
# trend = analysis.find_polynomial_trend(varying, polynomial_degree=degree)
# plt.figure()
# plt.plot(timeline, trend)
# # Step 3, remove trend from non-varying stars
# if not analysis.is_trend_constant(trend, degree):
#     detrended = analysis.detrend_dataset(non_varying, trend)

#     # Step 4, verify all non-varying stars are non-varying

#     detrended_varying, detrended_non_varying = analysis.find_varying_stars(
#         detrended)

#     plot.plot_and_save_all_4_grid(
#         detrended_non_varying, ("detrended_non_varying_" + file.stem))
#     plot.plot_and_save_all_4_grid(
#         detrended_varying, ("detrended_varying_" + file.stem))
# plot.plot_and_save_all_4_grid(varying, ("varying/varying_" + file.stem))
# plot.plot_and_save_all_4_grid(
#     non_varying, ("non_varying/non_varying_" + file.stem))
plot.plot_and_save_all_4_grid(df, file.stem)
