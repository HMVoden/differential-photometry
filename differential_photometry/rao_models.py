import importlib

import astropy.units as u
import numpy as np
from astropy.time import Time
from astropy.timeseries import BoxLeastSquares
from feets.preprocess import remove_noise
from scipy.stats import chisquare

import differential_photometry.rao_stats as stat


def box_least_squares(data: np.ndarray,
                      uncertainties: np.ndarray,
                      timeline: Time = None) -> np.ndarray:
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
        time = np.arange(0, samples, 1) * u.second
        # to push it to a single giant tophat
        time_middle = np.median(time) - (5 * u.second)
        # Tuning durations affects runtime and how many tophats/boxes appear
        durations = np.linspace(time_middle / 5, time_middle, 15)
    else:
        # Getting the effective exposure time
        deltaTime = timeline - timeline[0]
        time_middle = np.median(deltaTime) - 0.05 * np.median(deltaTime)
        durations = np.linspace(time_middle / 5, time_middle, 15)
    accumulated_results = []

    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        model = BoxLeastSquares(timeline, sample, uncertainty)
        periodogram = model.autopower(durations, frequency_factor=15)
        index = np.argmax(periodogram.power)  # The best option for a transit
        period = periodogram.period[index]
        t0 = periodogram.transit_time[index]
        duration = periodogram.duration[index]
        stats = model.compute_stats(period, duration, t0)
        model_fit = model.model(timeline, period, duration, t0)  # For graphing
        result = {"fitted_model": model_fit}

        if stats["transit_times"].size == 1:  # Filter
            result["varying"] = True
        else:
            result["varying"] = False
        accumulated_results.append(result)

    return np.array(accumulated_results)
