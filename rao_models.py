import numpy as np
import astropy.units as u

from feets.preprocess import remove_noise
from scipy.stats import chisquare
from astropy.timeseries import BoxLeastSquares
from astropy.time import Time

def chi_squared(data: np.ndarray, uncertainties: np.ndarray, timeline: Time) -> list:
    """ Cleans up data, normalizes data to unity and determines if 
    there's sufficient deviation from the median value via a chi squared test.
    TODO Filters if chi squared result is greater than 2
    
    Keyword arguments:
    data          -- a dataset of magnitudes for a sequence of stars, one star per row.
    timeline      -- the time from beginning to end of the data collection, not unique per star
    uncertainties -- error in the magnitudes
    """
    
    result = []
    for i, sample in enumerate(data):
        data_points = sample.shape[0]-1 #-1 since we're using the mean
        sigma = uncertainties[i]
        mean = np.mean(sample)
        chi = (1/data_points)*np.sum(((sample-mean)/sigma)**2)
        result.append(chi)
    return np.array(result)

def box_least_squares(data: np.ndarray, uncertainties: np.ndarray, timeline: Time = None) -> np.ndarray:
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
        result = {'fitted_model': model_fit}

        if(stats['transit_times'].size == 1): # Filter
            result['varying'] = True
        else:
            result['varying'] = False
        accumulated_results.append(result)
    
    return np.array(accumulated_results)