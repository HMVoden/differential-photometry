import numpy as np


def weighted_mean(sample: np.ndarray, uncertainty: np.ndarray):
    """Calculates the weighted mean with uncertainty of a data series as a numpy array

    Args:
        sample (np.ndarray): Array of values of the sample
        uncertainty (np.ndarray): array of the uncertainty the sample values have

    Returns:
        float: The calculated weighted mean
    """
    weight = np.sum(1/uncertainty**2)
    values_weighted = np.sum(sample/uncertainty**2)
    return values_weighted/weight
