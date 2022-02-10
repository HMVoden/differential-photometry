from pathlib import Path

import logging
from typing import Dict, List, Tuple


# def create_2x1_raw_diff_plot(
#     ds: xr.Dataset,
#     figure: plot_util.WorkerFigure,
#     plot_config: Dict,
#     mag_lim: float = None,
#     diff_lim: float = None,
# ) -> xr.Dataset:
#     axes = figure.get_next_axis()

#     # Raw Magnitude
#     plot_line_scatter(
#         x=ds["time"].data,
#         y=ds["mag"].data,
#         ylabel=plot_config["magnitude"]["ylabel"],
#         xlabel=plot_config["magnitude"]["xlabel"],
#         color=plot_config["magnitude"]["color"],
#         error=ds["error"].data,
#         axes=axes[0],
#         yrange=mag_lim,
#         plot_config=plot_config,
#     )
#     # Differential Magnitude
#     plot_line_scatter(
#         x=ds["time"].data,
#         y=ds["average_diff_mags"].data,
#         ylabel=plot_config["differential_magnitude"]["ylabel"],
#         xlabel=plot_config["differential_magnitude"]["xlabel"],
#         color=plot_config["differential_magnitude"]["color"],
#         error=ds["average_uncertainties"].data,
#         axes=axes[1],
#         yrange=diff_lim,
#         plot_config=plot_config,
#     )
#     figure.set_current_column_title(str(np.unique(ds["time.date"])[0]))
#     return ds


# def plot_line_scatter(
#     x: List[float],
#     y: List[float],
#     ylabel: str,
#     xlabel: str,
#     error: List[float],
#     axes: List[plt.Axes],
#     plot_config: Dict,
#     color: str = "blue",
#     yrange: Tuple[float, float] = None,
# ):
#     """Creates Two plots with inputted axes, one scatter and one line.
#     The scatter plot is made with errorbars, the line plot is made with fill between
#     error.

#     Parameters
#     ----------
#     x : List[float] or List[Time]
#         Numerical x-data.
#     y : List[float]
#         Numerical y-data
#     ylabel : str
#         Label of the y-axis
#     xlabel : str
#         Label of the x-axis
#     error : List[float]
#         Error of the y-data
#     axes : axes
#         Axis objects to plot in
#     color : str, optional
#         Colour information for plots, by default "blue"
#     yrange : Tuple[float, float], optional
#         The lower and upper limits of the y-axis for this set of plots, by default None
#     """
#     # For the fill between error bars
#     error_plus = y + error
#     error_neg = y - error

#     fill_between = {
#         "x": x,
#         "y1": error_plus,
#         "y2": error_neg,
#         "color": color,
#         **plot_config["error"]["fill"],
#     }
#     error_settings = {"x": x, **plot_config["error"]["bar"]}

#     sns.scatterplot(ax=axes, x=x, y=y, ci=None, color=color, animated=True)
#     axes.errorbar(y=y, yerr=error, label="Error", **error_settings)
#     axes.set_xlabel(xlabel)
#     axes.set_ylabel(ylabel)
#     axes.legend()
#     if yrange is not None:
#         axes.set_ylim(yrange)
