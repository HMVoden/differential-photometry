import numpy as np
import pandas as pd
import astropy.units as u

from pathlib import Path, PurePath
from numpy import sqrt
from astropy.timeseries import BoxLeastSquares, TimeSeries
from astropy.time import Time, TimeDelta
from feets.preprocess import remove_noise
from feets import FeatureSpace

def subtract_all_magnitudes(magnitudes: np.ndarray) -> np.ndarray:
    all_magnitudes_subtracted = [] # List so appending is not memory-intensive
    for index, column in enumerate(magnitudes.T): # Index so we can remove active column
        delta = np.delete(magnitudes, index, axis=1).T - column # Remove 'active' column, subtract active from every other column
        all_magnitudes_subtracted.append(delta)
    return np.array(all_magnitudes_subtracted) # Return np.array for modification later

def calculate_all_uncertainties(errors: np.ndarray) -> np.ndarray:
    all_uncertainties = [] # List so appending is not memory-intensive
    for index, column in enumerate(errors.T): # Index so we can remove active column
        uncertainty = sqrt(np.delete(errors, index, axis=1).T**2 + column**2) # Remove 'active' column, get uncertainty for each column
        all_uncertainties.append(uncertainty) 
    return np.array(all_uncertainties) # Return np.array for modification later

def normalize(data: np.ndarray) -> np.ndarray: # Brings data to be between 0-1
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data-data_min)/(data_max - data_min)
    return normalized

def box_model_data(data: np.ndarray, uncertainties: np.ndarray, timeline: Time = None) -> np.ndarray:
    if timeline is None:
        samples = data.shape[1]
        time = np.arange(0,  samples, 1)*u.second
        time_middle = np.median(time)-(5*u.second) # to push it to a single giant tophat
        durations = np.linspace(time_middle/5, time_middle, 15) # Tuning durations affects runtime and how many tophats/boxes appear
    else:
        deltaTime = timeline - timeline[0]
        time_middle = np.median(deltaTime) - 0.05*np.median(deltaTime) 
        durations = np.linspace(time_middle/5, time_middle, 15)
    accumulated_results = []
    
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        model = BoxLeastSquares(timeline, sample, uncertainty)
        periodogram = model.autopower(durations, frequency_factor=15)
        index = np.argmax(periodogram.power)
        period = periodogram.period[index]
        t0 = periodogram.transit_time[index]
        duration = periodogram.duration[index]
        stats = model.compute_stats(period, duration, t0)
        model_fit = model.model(timeline, period, duration, t0)

        if(stats['transit_times'].size == 1):
            result = {'name': i,
                    'best_fit_values': {'index': index, 'period': period, 'transit_time':t0, 'duration': duration},
                    'data': sample,
                    'uncertainty': uncertainty,
                    'stats': stats,
                    'fitted_model': model_fit,
                    'time': timeline}
            accumulated_results.append(result)
    
    return np.array(accumulated_results)

def all_feets_indices(data: np.ndarray, timeline: Time, uncertainties: np.ndarray) -> list:
    result = [] #Easier to append to a list
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        time, sample, uncertainty = remove_noise(timeline, sample, uncertainty, error_limit=3, std_limit=5)
        lc = (time, sample, uncertainty)
        feature_space = FeatureSpace(data=['time','magnitude','error'])
        features, values = feature_space.extract(*lc)
        result.append(dict(zip(features, values)))
    return result

def extract_data(filename: str) -> pd.DataFrame:
    # Gives us a clean and workable dataframe
    data_path = PurePath(filename)
    if data_path.suffix == '.xlsx':
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '_').str.replace(')', '').str.replace('<', '').str.replace('>','')
    # Cleanup of headers, could be made more succinct with a simple REGEX
    desired_column_names = np.array(['obj', 'name', 'mag', 'error', 'error_t', 's/n', 'x', 'y', 'date', 'time', 'jd'])
    extracted_column_names = df.columns
    intersection = np.intersect1d(desired_column_names, extracted_column_names) #Finds common column names
    return df[intersection] # Returns only column names we want.

def extract_samples_stars(dataframe: pd.DataFrame) -> int:
    # Calculates how many stars we're working with and how many times each is sampled.
    rows = dataframe.shape[0]
    if 'obj' in dataframe.columns:
        num_stars = dataframe['obj'].nunique()
    elif 'name' in dataframe.columns:
        num_stars = dataframe['name'].nunique()
    samples = int(rows/num_stars)
    return num_stars, samples
