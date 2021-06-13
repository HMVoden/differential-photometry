import numpy as np

from numpy import sqrt
from feets.preprocess import remove_noise
from feets import FeatureSpace
from astropy.time import Time, TimeDelta

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