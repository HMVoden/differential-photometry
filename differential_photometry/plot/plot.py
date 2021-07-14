import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from os import PathLike
from typing import Callable, Dict, List, Tuple

import config.manager as config
import differential_photometry.data.input_output as io
import differential_photometry.data.utilities as data_util
import differential_photometry.progress_bars as bars
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure

manager = None
status = None


def plot_and_save_all(df: pd.DataFrame):
    """Setup function for plotting and saving the entire dataframe as a series of graphs

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with mag, average_diff_mags, error and average uncertainty as numerical columns
    uniform_y_axis : bool, optional
        Sets the entire dataset to be graphed with the same y-limit plus or minus from median, by default False
    split : bool, optional
        Splits the dataframe into varying and non-varying, by default False
    """
    plot_config = config.get("plotting")
    uniform_y_axis = config.get("uniform")
    correct = config.get("offset")
    mag_max_variation, diff_max_variation = get_max_variation(df)

    #end ifs
    to_plot = generate_data_folders(df=df,
                                    uniform_y_axis=uniform_y_axis,
                                    correct=correct)
    pbar_plot = bars.get_progress_bar(name="plot_to_folder",
                                      total=len(to_plot),
                                      desc="Plotting folder",
                                      unit="folder",
                                      color="purple",
                                      leave=False)
    for frame, folder in to_plot:
        logging.info("Writing to folder %s", folder)
        star_frames = frame.groupby("id")
        multiprocess_save(star_frames,
                          correct=correct,
                          mag_max_variation=mag_max_variation,
                          diff_max_variation=diff_max_variation,
                          output_folder=folder,
                          plot_config=plot_config)
        pbar_plot.update()


def generate_data_folders(
        df: pd.DataFrame, uniform_y_axis: bool,
        correct: bool) -> List[Tuple[pd.DataFrame, PathLike]]:
    result = []
    # Need both output folders
    for frame in data_util.split_varying(df):
        folder = io.generate_graph_output_path(
            corrected=correct,
            uniform=uniform_y_axis,
            varying=frame.varying.all(),
            brief=frame.graph_intra.all(),
        )
        result.append((frame, folder))

    return result


def get_max_variation(df: pd.DataFrame) -> Tuple[float, float]:
    mag_y_scale = config.get("mag_y_scale")
    diff_y_scale = config.get("diff_y_scale")
    uniform_y_axis = config.get("uniform")

    mag_max_variation = None
    diff_max_variation = None
    if mag_y_scale is not None or diff_y_scale is not None:
        mag_max_variation = mag_y_scale
        diff_max_variation = diff_y_scale
        if mag_y_scale is None or diff_y_scale is None:
            logging.warning(
                "The magnitude or differential magnitude plotting scale is not set."
            )
            logging.warning("Continuing with defaults for unset scale.")

    if uniform_y_axis is True:
        # Calculate the largest deviation along the y-axis
        # for the entire dataset
        columns = ["mag", "average_diff_mags"]
        max_variation = data_util.get_largest_range(
            **data_util.arrange_time_star(df, columns))

        # Divide by 2 to keep most data in viewing range as
        # this encompasses the entire range (half above, half below)
        mag_max_variation = np.round(max_variation["mag"] / 2, decimals=1)
        diff_max_variation = np.round(max_variation["average_diff_mags"] / 2,
                                      decimals=1)
    logging.info("Magnitude y-axis range is: %s", mag_max_variation)
    logging.info("Differential y-axis range is: %s", diff_max_variation)
    return mag_max_variation, diff_max_variation


def multiprocess_save(star_frames: pd.DataFrame,
                      plot_config: Dict,
                      correct: bool,
                      mag_max_variation: float = None,
                      diff_max_variation: float = None,
                      output_folder: PathLike = None):
    """Runner function, sets up multiprocess graphing for system

    Parameters
    ----------
    star_frames : pd.DataFrame
        Dataframes that contain all necessary star data
    mag_max_variation : float, optional
        The maximum magnitude variation of the dataset, for y-lim, by default None
    diff_max_variation : float, optional
        The maximum differential magnitude variation of the dataset, for y-lim, by default None
    save : bool, optional
        Switch to save or graph and display, by default False
    """
    bars.status.update(demo="Plotting and saving stars")
    pbar = bars.get_progress_bar(name="plot_and_save",
                                 total=len(star_frames),
                                 desc="  Plotting and saving stars",
                                 unit="stars",
                                 color="magenta",
                                 leave=False)
    # Mulitprocess to speed up awful plotting code
    plot_function = partial(create_4x1_raw_diff_plot,
                            mag_max_variation=mag_max_variation,
                            diff_max_variation=diff_max_variation,
                            correct=correct,
                            plot_config=plot_config)
    saving_function = partial(save_figure, output_folder=output_folder)
    seaborn_config = plot_config["seaborn"]
    # for frame in star_frames:
    #     build_and_save_figure(frame,
    #                           save_function=saving_function,
    #                           plot_function=plot_function,
    #                           seaborn_config=seaborn_config)
    #     pbar.update()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(build_and_save_figure,
                            data=frame,
                            save_function=saving_function,
                            plot_function=plot_function,
                            seaborn_config=seaborn_config)
            for frame in star_frames
        }
        for future in as_completed(futures):
            pbar.update()


def build_and_save_figure(data: pd.DataFrame,
                          plot_function: Callable[[pd.DataFrame], Tuple[Figure,
                                                                        str]],
                          save_function: Callable[[Figure],
                                                  bool], seaborn_config: Dict):
    # Needs to be set here so each worker
    # Has the same settings
    sns.set_theme(**seaborn_config)
    fig, name = plot_function(data)
    save_function(fig, name)


def save_figure(fig: Figure, file_name: str, output_folder: PathLike):
    """Generates output path, calls plotting function then saves figure to specified file

    """
    if not output_folder.exists():
        logging.info("Creating directory %s", output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder.joinpath(file_name + ".png")
    fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")
    plt.close(fig)
    return True


def create_4x1_raw_diff_plot(
    star,
    plot_config: Dict,
    correct: bool,
    mag_max_variation=None,
    diff_max_variation=None,
):
    """Creates a column plot of 2 scatter and 2 line plots, one of each is for raw
    magnitude and one of each is for differential magnitude.
    Requires errors for both.

    Parameters
    ----------
    star : pd.Dataframe
        Dataframe containing necessary values, specifically
        numerical columns "mag", "average_diff_mags",
        "error", "average_uncertainty"
    mag_max_variation : float, optional
        The maximum dataset variation found in a single day for raw magnitude, by default None
    diff_max_variation : float, optional
        The maximum dataset variation found in a single day for differential magnitude, by default None

    Returns
    -------
    figure
        Matplotlib figure of a column representing a timeseries day
    """
    star_name = star[0]
    star = star[1]
    if mag_max_variation != None and diff_max_variation != None:
        mag_median = np.median(star["mag"])
        diff_median = np.median(star["average_diff_mags"])
        mag_lim = (mag_median - mag_max_variation,
                   mag_median + mag_max_variation)
        diff_lim = (diff_median - diff_max_variation,
                    diff_median + diff_max_variation)
    else:
        mag_lim = None
        diff_lim = None
    #end if
    mag_y = "mag"
    diff_y = "average_diff_mags"
    if correct is True:
        mag_y = "c_" + mag_y
        diff_y = "c_" + diff_y

    day_frames = data_util.group_by_year_month_day(star)
    days = len(day_frames)
    fig, axes = plt.subplots(nrows=4,
                             ncols=days,
                             figsize=(5 * days, 15),
                             sharex=False)
    if days == 1:
        axes = np.asanyarray(axes)
    axes = np.asanyarray(axes).transpose()
    # This is a bad code smell, very slow.
    for i, frame_dict in enumerate(day_frames):
        frame = frame_dict[1]
        day = frame_dict[0]
        logging.debug("Graphing star day %s", day)
        if days > 1:
            day_ax = axes[i]
        else:
            day_ax = axes

        # Raw Magnitude
        plot_line_scatter(x=frame["time"],
                          y=frame[mag_y],
                          ylabel=plot_config["magnitude"]["ylabel"],
                          xlabel=plot_config["magnitude"]["xlabel"],
                          color=plot_config["magnitude"]["color"],
                          error=frame["error"],
                          axes=day_ax[:2],
                          yrange=mag_lim,
                          plot_config=plot_config)
        # Differential Magnitude
        plot_line_scatter(
            x=frame["time"],
            y=frame[diff_y],
            ylabel=plot_config["differential_magnitude"]["ylabel"],
            xlabel=plot_config["differential_magnitude"]["xlabel"],
            color=plot_config["differential_magnitude"]["color"],
            error=frame["average_uncertainties"],
            axes=day_ax[2:],
            yrange=diff_lim,
            plot_config=plot_config)
        day_ax[0].set_title(str(day))

        # end day loop
    if days > 1:
        for col in axes:
            col[0].get_shared_x_axes().join(*col)
        for row in axes.transpose():
            row[0].get_shared_y_axes().join(*row)
        for ax in axes.flat:
            ax.xaxis.set_major_formatter(  # set display of time
                mdates.DateFormatter(plot_config["time"]["format"]))
            ax.label_outer()
    else:
        axes[0].get_shared_x_axes().join(*axes)

        fig.subplots_adjust(wspace=0.025)
    fig.suptitle(("Raw and differential magnitude of star " + star_name))
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig, star_name


def plot_line_scatter(x: List[float],
                      y: List[float],
                      ylabel: str,
                      xlabel: str,
                      error: List[float],
                      axes: List[plt.Axes],
                      plot_config: Dict,
                      color: str = "blue",
                      yrange: Tuple[float, float] = None):
    """Creates Two plots with inputted axes, one scatter and one line.
    The scatter plot is made with errorbars, the line plot is made with fill between
    error.

    Parameters
    ----------
    x : List[float] or List[Time]
        Numerical x-data.
    y : List[float]
        Numerical y-data
    ylabel : str
        Label of the y-axis
    xlabel : str
        Label of the x-axis
    error : List[float]
        Error of the y-data
    axes : axes
        Axis objects to plot in
    color : str, optional
        Colour information for plots, by default "blue"
    yrange : Tuple[float, float], optional
        The lower and upper limits of the y-axis for this set of plots, by default None
    """
    # For the fill between error bars
    error_plus = y + error
    error_neg = y - error

    fill_between = {
        "x": x,
        "y1": error_plus,
        "y2": error_neg,
        "color": color,
        **plot_config["error"]["fill"]
    }
    error_settings = {"x": x, **plot_config["error"]["bar"]}

    sns.lineplot(ax=axes[0], x=x, y=y, ci=None, color=color)
    axes[0].fill_between(**fill_between)
    sns.scatterplot(ax=axes[1], x=x, y=y, ci=None, color=color)
    axes[1].errorbar(y=y, yerr=error, label="Error", **error_settings)
    for ax in axes:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        if yrange is not None:
            ax.set_ylim(yrange)
