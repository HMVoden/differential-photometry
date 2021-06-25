import numpy as np


def weighted_mean(sample, uncertainty=None):
    """Calculates the weighted mean with uncertainty of a data series as a numpy array

    Args:
        sample (np.ndarray): Array of values of the sample
        uncertainty (np.ndarray): array of the uncertainty the sample values have

    Returns:
        float: The calculated weighted mean
    """
    if uncertainty is None:
        uncertainty = 1  # now it is just a calculation of the mean
    weight = np.sum(1/uncertainty**2)
    values_weighted = np.sum(sample/uncertainty**2)
    return values_weighted/weight


def reduced_chi_square(data: np.ndarray, uncertainty=None, expected=None, parameters_estimated=None):
    """ Calculates reduced chi squared versus hypothesis that dataset follows its weighted mean.

    Keyword arguments:
    data (np.ndarray)          -- Data from sequence
    uncertainties (np.ndarray) -- (Optional) error in the data
    """
    # This is ugly and can be handled better
    if parameters_estimated is None:
        parameters_estimated = 0
    if uncertainty is None:
        parameters_estimated += 1
        variance = np.var(data, ddof=1)
    if expected is None:
        parameters_estimated += 1
        expected = np.median(data)
    if uncertainty is not None:
        variance = uncertainty**2

    dof = data.shape[0] - parameters_estimated
    chi = np.sum(((data-expected)**2/variance))/dof
    return chi
