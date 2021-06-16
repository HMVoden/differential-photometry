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


def reduced_chi_square(data: np.ndarray, uncertainty: np.ndarray) -> list:
    """ Calculates reduced chi squared versus hypothesis that dataset follows its weighted mean.
    Assumes that error is heteroscedastic and thus weighted mean is necessary.

    Keyword arguments:
    data          -- Data from sequence
    uncertainties -- error in the data
    """

    dof = data.shape[0]-1  # -1 since we're using the mean
    expected = weighted_mean(data, uncertainty)
    chi = np.sum(((data-expected)**2/uncertainty**2))/dof
    return chi
