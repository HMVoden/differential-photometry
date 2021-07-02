import numpy as np
import toml

from arch.unitroot import ADF, DFGLS, ZivotAndrews, KPSS

from scipy.stats import chisquare

stats_config = toml.load("config/stats.toml")


def reduced_chi_square(data,
                       error=None,
                       expected=None,
                       parameters_estimated=None):
    """ Calculates reduced chi squared versus hypothesis that dataset follows its weighted mean.

    Keyword arguments:
    data (np.ndarray)          -- Data from sequence
    uncertainties (np.ndarray) -- (Optional) error in the data
    """
    # This is ugly and can be handled better
    data = np.asanyarray(data)
    if parameters_estimated is None:
        parameters_estimated = 0
    if error is None:
        parameters_estimated += 1
        variance = np.var(data, ddof=1)
    if error is not None:
        uncertainty = np.asanyarray(error)
        variance = uncertainty**2
    if expected is None:
        parameters_estimated += 1
        expected = np.average(data, weights=(1 / error**2))

    dof = data.shape[0] - parameters_estimated - 1
    chi = np.sum(((data - expected)**2 / variance)) / dof
    # print(chi)
    return chi


def regular_chi_square(data, error=None):
    expected_switch = stats_config["chisquared"]["expected"]
    ddof = stats_config["chisquared"]["ddof"]
    expected = None
    if expected_switch == "mean":
        expected = np.average(data)
    elif expected_switch == "median":
        expected = np.median(data)
    elif expected_switch == "weighted_mean":
        expected = np.average(data, weights=(1 / error**2))

    result = chisquare(f_obs=data, f_exp=expected, ddof=ddof)
    print(result)
    return result[1]  #p-value


def augmented_dfuller(data):
    result = ADF(data, **stats_config["adfuller"])
    # print(result)
    return result.pvalue  #p-value


def kpss(data):
    result = KPSS(data, **stats_config["kpss"])
    return result.pvalue  #p-value


def zastat(data):
    result = ZivotAndrews(data, **stats_config["zivot_andrews"])
    return result.pvalue  #p-value


def adf_gls(data):
    result = DFGLS(data, **stats_config["adf_gls"])
    return result.pvalue
