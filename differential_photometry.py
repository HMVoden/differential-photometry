# %%
import numpy as np
import pandas as pd
import rao_utilities as util
import rao_plotting as plot
import rao_models as model
import rao_stats as stat
import rao_math as m
import warnings
import importlib
import matplotlib.pyplot as plt

from feets import ExtractorWarning
from pathlib import PurePath
from astropy.modeling import models, fitting
from scipy.signal import detrend

importlib.reload(util)
importlib.reload(plot)
importlib.reload(model)
importlib.reload(m)
importlib.reload(stat)

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
# Chi squared test
df['varying'] = False
df['chisquared'] = 0.0
stars = df['name'].unique()
mags = df['mag'].to_numpy(dtype='float64').reshape(
    num_samples, num_stars).transpose()
errors = df['error'].to_numpy(dtype='float64').reshape(
    num_samples, num_stars).transpose()
all_chi = []
for i, sample in enumerate(mags):
    error = errors[i]
    chi = stat.reduced_chi_square(sample, error)
    if chi > 7.0:
        df.loc[df['name'] == stars[i], 'varying'] = True
        df.loc[df['name'] == stars[i], 'chisquared'] = chi
    else:
        df.loc[df['name'] == stars[i], 'chisquared'] = chi
    all_chi.append(chi)
varying = df[df['varying'] == True]
non_varying = df[df['varying'] == False]

# Step 2, find trend in non-varying stars
num_stars, num_samples = util.extract_samples_stars(non_varying)
non_varying_mags = non_varying['mag'].to_numpy(dtype='float64').reshape(
    num_samples, num_stars)
average_mag = np.mean(non_varying_mags, axis=1)
non_varying_error = non_varying['error'].to_numpy(dtype='float64').reshape(
    num_samples, num_stars)
average_error = np.sum(non_varying_error**2, axis=1)/num_stars

weight = 1/average_error**2
degree = 3

test_mag = non_varying_mags.transpose()[0]
test_error = non_varying_error.transpose()[0]

fit = fitting.LinearLSQFitter()
poly = models.Chebyshev1D(degree=degree)
fitted_poly = fit(
    model=poly, x=non_varying['jd'].unique(), y=average_mag, weights=weight)

plt.figure()
plt.plot(non_varying['jd'].unique(), test_mag, label='data')
plt.plot(non_varying['jd'].unique(), fitted_poly(
    non_varying['jd'].unique()), label='model')
plt.legend()

general_parameters = dict(zip(fitted_poly.param_names, fitted_poly.parameters))
copied_domain = fitted_poly.domain
general_parameters['c0'] = 0

new_model = models.Chebyshev1D(
    degree=degree, domain=copied_domain, **general_parameters)

y = m.normalize_to_median(new_model(non_varying['jd'].unique()))

plt.figure()
plt.plot(non_varying['jd'].unique(), test_mag, label='data')
plt.plot(non_varying['jd'].unique(), (test_mag - y), label='modified data')
plt.legend()


# Step 3, remove trend from non-varying stars

corrected_non_varying_mags = non_varying_mags.transpose() - \
    new_model(non_varying['jd'].unique())
corrected_non_varying_mags = corrected_non_varying_mags.reshape(num_samples *
                                                                num_stars, 1)
non_varying = non_varying.assign(mag=corrected_non_varying_mags)

# Step 4, verify all non-varying stars are non-varying
# plot.plot_and_save_all_4_grid(non_varying, file.stem)

# plot.plot_and_save_all_4_grid(df, file.stem)

# %%
