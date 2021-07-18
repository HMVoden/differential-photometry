from typing import List

from feets import FeatureSpace
from feets.preprocess import remove_noise


def calculate_all_feets_indices(
    data: List[float], timeline: List[float], uncertainties: List[float]
) -> List:
    """Runs through an entire set of datasets and calculates every
    single feature detailed in the FEETS featurelist that's relevant to time, magnitude and error

    Parameters
    ----------
    data : np.ndarray
        Numerical data to for features to be extracted from
    timeline : Time
        Timeline of the timeseries in question
    uncertainties : np.ndarray
        Error in the data (sigma)

    Returns
    -------
    list
        Every feature extractable from the FEETs library that handles time, magnitude and error
    """

    result = []  # Easier to append to a list
    for i, sample in enumerate(data):
        uncertainty = uncertainties[i]
        time, sample, uncertainty = remove_noise(
            timeline, sample, uncertainty, error_limit=3, std_limit=5
        )
        lc = (time, sample, uncertainty)
        feature_space = FeatureSpace(data=["time", "magnitude", "error"])
        features, values = feature_space.extract(*lc)
        result.append(dict(zip(features, values)))
    return result
