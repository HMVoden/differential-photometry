import numpy as np
import pandas as pd
import astropy.units as u
import logging

from pathlib import Path, PurePath
from numpy import float64, sqrt
from astropy.timeseries import BoxLeastSquares, TimeSeries
from astropy.time import Time, TimeDelta
from feets.preprocess import remove_noise
from feets import FeatureSpace
from scipy.stats import chisquare


def subtract_all_magnitudes(magnitudes: np.ndarray) -> np.ndarray:
    """For each star inputted into this function, this will take that star column, remove it from the dataset
    then subtract it from the other stars, creating an entire list of numpy arrays with a series of 'target stars'
    for use in differential photometry
    
    Keyword arguments:
    magnitudes -- a numpy array of star magnitudes, ordered by row=time, magnitude=star
    """
    
    all_magnitudes_subtracted = [] # List so appending is not memory-intensive
    for index, column in enumerate(magnitudes.T): # Index so we can remove active column
        delta = np.delete(magnitudes, index, axis=1).T - column # Remove 'active' column, subtract active from every other column
        all_magnitudes_subtracted.append(delta)
    return np.array(all_magnitudes_subtracted)

def calculate_all_uncertainties(errors: np.ndarray) -> np.ndarray:
    """For each star's error inputted into this function, this will take that error column, remove it from the dataset
    then square roots the sum the squares of the other columns and the removed one, 
    creating an entire list of numpy arrays with a series of 'target star errors' for use in differential photometry
    
    Keyword arguments:
    errors -- a numpy array of star error, ordered by row=time, column=error
    """
    all_uncertainties = [] # List so appending is not memory-intensive
    for index, column in enumerate(errors.T): # Index so we can remove active column
        uncertainty = sqrt(np.delete(errors, index, axis=1).T**2 + column**2) # Remove 'active' column, get uncertainty for each column
        all_uncertainties.append(uncertainty) 
    return np.array(all_uncertainties)

def normalize(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and normalizes it to between 0-1 """
    data_min = np.min(data)
    data_max = np.max(data)
    normalized = (data-data_min)/(data_max - data_min)
    return normalized

def normalize_to_median(data: np.ndarray) -> np.ndarray:
    """ Takes a dataset and brings the median to 1"""
    median = np.median(data)
    return data/median

def model_box_data(data: np.ndarray, uncertainties: np.ndarray, timeline: Time = None) -> np.ndarray:
    """ Takes a dataset with uncertainties and a timeline, applies a box least squares model to it,
    then filters the data by if the number of transits is equal to one, approximating a dip or increase
    in the magnitude of the target star over time.
    
    This is a naive approach to the problem, and does not have a great success rate.
    Keyword arguments:
    data          -- a dataset of magnitudes for a sequence of stars, one star per row.
    timeline      -- the time from beginning to end of the data collection, not unique per star
    uncertainties -- error in the magnitudes
    """
    if timeline is None:
        samples = data.shape[1]
        time = np.arange(0,  samples, 1)*u.second
        time_middle = np.median(time)-(5*u.second) # to push it to a single giant tophat
        durations = np.linspace(time_middle/5, time_middle, 15) # Tuning durations affects runtime and how many tophats/boxes appear
    else:
        deltaTime = timeline - timeline[0] # Getting the effective exposure time
        time_middle = np.median(deltaTime) - 0.05*np.median(deltaTime) 
        durations = np.linspace(time_middle/5, time_middle, 15)
    accumulated_results = []
    
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        model = BoxLeastSquares(timeline, sample, uncertainty)
        periodogram = model.autopower(durations, frequency_factor=15)
        index = np.argmax(periodogram.power) #The best option for a transit
        period = periodogram.period[index]
        t0 = periodogram.transit_time[index]
        duration = periodogram.duration[index]
        stats = model.compute_stats(period, duration, t0)
        model_fit = model.model(timeline, period, duration, t0) # For graphing

        if(stats['transit_times'].size == 1): # Filter
            result = {'name': i,
                    'best_fit_values': {'index': index, 'period': period, 'transit_time':t0, 'duration': duration},
                    'data': sample,
                    'uncertainty': uncertainty,
                    'stats': stats,
                    'fitted_model': model_fit,
                    'time': timeline} # Data construct for ease of use.
            accumulated_results.append(result)
    
    return np.array(accumulated_results)

def model_chi_squared(data: np.ndarray, timeline: Time, uncertainties: np.ndarray) -> list:
    """ Cleans up data, normalizes data to unity and determines if 
    there's sufficient deviation from the median value via a chi squared test.
    Filters if chi squared result is greater than 2
    
    Keyword arguments:
    data          -- a dataset of magnitudes for a sequence of stars, one star per row.
    timeline      -- the time from beginning to end of the data collection, not unique per star
    uncertainties -- error in the magnitudes
    """
    
    result = []
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        _, sample, uncertainty = remove_noise(timeline, sample, uncertainty, error_limit=3, std_limit=5)
        data_points = sample.shape[0]-1
        expect = np.mean(sample)
        chi = chisquare(sample, expect, ddof=data_points)
        result.append(chi[0])
    return np.array(result)

def calculate_all_feets_indices(data: np.ndarray, timeline: Time, uncertainties: np.ndarray) -> list:
    """ Runs through an entire set of datasets and calculates every 
    single feature detailed in the FEETS featurelist that's relevant to time, magnitude and error
    
    Keyword arguments:
    data          -- a dataset of magnitudes for a sequence of stars, one star per row.
    timeline      -- the time from beginning to end of the data collection, not unique per star
    uncertainties -- error in the magnitudes
    """
    
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
    """ Assuming there are headers in the data file, this takes the filename opens it and reads it
    into a pandas dataframe, cleans the headers to make it all lowercase with no parenthesis and returns only
    the columns we're interested in.
    
    Keyword arguments:
    filename -- the name of the file to be opened and read
    """

    data_path = PurePath(filename)
    if data_path.suffix == '.xlsx': # This way we can ignore if it's a csv or excel file
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '_').str.replace(')', '').str.replace('<', '').str.replace('>','')
    # Cleanup of headers, could be made more succinct with a simple REGEX
    desired_column_names = np.array(['obj', 'name', 'mag', 'error', 'error_t', 's/n', 'x', 'y', 'date', 'time', 'jd'])
    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this script.
    extracted_column_names = df.columns
    intersection = np.intersect1d(desired_column_names, extracted_column_names) #Finds common column names
    return clean_stars_data(df[intersection])

def extract_samples_stars(dataframe: pd.DataFrame) -> int:
    """Determines and returns the number of different star samples and number of stars as integers"""
    rows = dataframe.shape[0]
    if 'obj' in dataframe.columns: # Since this is what we normally see in the .csvs
        num_stars = dataframe['obj'].nunique()
    elif 'name' in dataframe.columns: # Backup in case of other Mira data
        num_stars = dataframe['name'].nunique()
    samples = int(rows/num_stars)
    return num_stars, samples

def clean_stars_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Ensures that the columns mag, error, error_t and either obj or name are present.
    Then makes sure that the mag, error and error_t are viable and in the right format.
    Removes all stars with any mag value of "Flux<0"
    
    Keyword Arguments:
    dataframe -- A pandas dataframe containing the proper column names
    """
    required_columns = ['mag', 'error', 'error_t']
    for col in required_columns:
        if col not in dataframe.columns:
            raise KeyError("ERROR: Unable to continue program, missing critical column: {0}".format(col))
    if 'name' not in dataframe.columns and 'obj' not in dataframe.columns:
        raise KeyError("""ERROR: Unable to continue program, 
                    missing name/object columns for number of star
                    calculations""")
    
    datatypes = dataframe.dtypes
    if not isinstance(datatypes['mag'], float64): # Could make this apply to error and error_t too
        logging.warning("column {0} is not a numerical type, attempting to fix".format("mag"))
        bad_mags = dataframe[(dataframe.mag == "Flux<0")] # First instance of bad data
        if 'name' in dataframe.columns:
            stars_removed = bad_mags.name.unique()
            star_rows = dataframe[(dataframe['name'].isin(stars_removed))]
        if 'obj' in dataframe.columns:
            stars_removed = bad_mags.obj.unique()
            star_rows = dataframe[(dataframe['obj'].isin(stars_removed))]
        logging.warning("removing star(s) {0} from dataset".format(stars_removed))
        dataframe = dataframe.drop(index=star_rows.index)
    return dataframe