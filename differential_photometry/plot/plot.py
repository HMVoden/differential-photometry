import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
from os import PathLike
from pathlib import Path

import differential_photometry.utilities.math as math_utils
import matplotlib.dates as mdates  # TODO Configure date display on plots
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import toml
import differential_photometry.config as config
from differential_photometry.utilities.data import arrange_time_star, split_on, split_varying
from differential_photometry.utilities.input_output import \
    generate_graph_output_path

import differential_photometry.utilities.progress_bars as bars

# Get config information
plot_config = toml.load("config/plotting.toml")
seaborn_config = plot_config["seaborn"]
magnitude_config = plot_config["magnitude"]
differential_magnitude_config = plot_config["differential_magnitude"]
bar_error_config = plot_config["error"]["bar"]
fill_error_config = plot_config["error"]["fill"]

manager = None
status = None


def plot_and_save_all(df: pd.DataFrame,
                      uniform_y_axis: bool = False,
                      split: bool = False,
                      corrected: bool = False,
                      output_folder: Path = None,
                      mag_y_scale: float = None,
                      diff_y_scale: float = None):
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
    to_plot = []
    if mag_y_scale is not None or diff_y_scale is not None:
        mag_max_variation = mag_y_scale
        diff_max_variation = diff_y_scale
        if uniform_y_axis is True:
            logging.warning(
                "Manual y-axis scaling and uniform y-axis flag are both set, disabling uniform."
            )
            uniform_y_axis = False
        if mag_y_scale is None or diff_y_scale is None:
            logging.warning(
                "The magnitude or differential magnitude plotting scale is not set."
            )
            logging.warning("Continuing with defaults for unset scale.")
        logging.info("Maximum raw magnitude difference is: %s",
                     mag_max_variation)
        logging.info("Maximum differential magnitude difference is: %s",
                     diff_max_variation)
    if uniform_y_axis is True:
        # Calculate the largest deviation along the y-axis
        # for the entire dataset
        columns = ["mag", "average_diff_mags"]
        max_variation = math_utils.get_largest_range(
            **arrange_time_star(df, columns))

        # Divide by 2 to keep most data in viewing range as
        # this encompasses the entire range (half above, half below)
        mag_max_variation = np.round(max_variation["mag"] / 2, decimals=1)
        diff_max_variation = np.round(max_variation["average_diff_mags"] / 2,
                                      decimals=1)

        logging.info("Maximum raw magnitude difference is: %s",
                     mag_max_variation)
        logging.info("Maximum differential magnitude difference is: %s",
                     diff_max_variation)
    else:
        mag_max_variation = None
        diff_max_variation = None
    if split is True:
        # Need both output folders
        non_varying, briefly_varying, varying = split_varying(df)
        varying_output_folder = generate_graph_output_path(
            corrected=corrected,
            split=True,
            varying=True,
            uniform=uniform_y_axis)
        brief_output_folder = generate_graph_output_path(
            corrected=corrected,
            split=True,
            varying=True,
            uniform=uniform_y_axis,
            brief=True)
        non_varying_output_folder = generate_graph_output_path(
            corrected=corrected,
            split=True,
            varying=False,
            uniform=uniform_y_axis)
        to_plot.append((non_varying, non_varying_output_folder))
        to_plot.append((varying, varying_output_folder))
        to_plot.append((briefly_varying, brief_output_folder))
    else:
        output_folder = generate_graph_output_path(corrected=corrected,
                                                   split=False,
                                                   varying=False,
                                                   uniform=uniform_y_axis)
        to_plot.append((df, output_folder))
    #end ifs

    pbar_plot = bars.get_progress_bar(name="plot_to_folder",
                                      total=len(to_plot),
                                      desc="Plotting folder",
                                      unit="folder",
                                      color="purple",
                                      leave=False)
    for frame, folder in to_plot:
        logging.info("Writing to folder %s", folder)
        star_frames = frame.groupby("id")
        raw_diff_magnitudes(star_frames,
                            mag_max_variation=mag_max_variation,
                            diff_max_variation=diff_max_variation,
                            output_folder=folder)
        pbar_plot.update()


def raw_diff_magnitudes(star_frames: pd.DataFrame,
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
    config.pbar_status.update(demo="Plotting and saving stars")
    pbar = bars.get_progress_bar(name="plot_and_save",
                                 total=len(star_frames),
                                 desc="  Plotting and saving stars",
                                 unit="stars",
                                 color="magenta",
                                 leave=False)
    # Mulitprocess to speed up awful plotting code
    if output_folder is not None:
        plot_function = partial(
            create_4x1_raw_diff_plot,
            mag_max_variation=mag_max_variation,
            diff_max_variation=diff_max_variation,
        )
        saving_function = partial(save_plots,
                                  plot_function=plot_function,
                                  output_folder=output_folder)
        # for name, frame in star_frames:
        #     saving_function([name, frame])
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(saving_function, frame)
                for frame in star_frames
            }
            for future in as_completed(futures):
                pbar.update()

    else:
        # for group in star_frames:
        #     show_plots(group)
        # list(map(show_plots, star_frames))
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(show_plots, frame)
                for frame in star_frames
            }
            for future in as_completed(futures):
                pbar.update()
        # pass


def save_plots(data: pd.DataFrame, plot_function, output_folder):
    """Generates output path, calls plotting function then saves figure to specified file

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe containing numerical data for plot
    plot_function : Callable[[pd.DataFrame, int=None, int=None], figure]
        Function that generates the plots and figures to be saved
    """
    # Needs to be set here so each worker
    # Has the same settings
    sns.set_theme(**seaborn_config)
    logging.info("Plotting and saving %s", data[0])
    if not output_folder.exists():
        logging.info("Creating directory %s", output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder.joinpath(data[0] + ".png")
    logging.debug("Output file: %s", output_file)
    fig = plot_function(data[1])
    fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")
    plt.close(fig)
    return


def show_plots(data, plot_function):
    """Runs plotting function then shows generated figure.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe containing numerical data for plot
    plot_function : Callable[[pd.DataFrame, int=None, int=None], figure]
        Function that generates the plots and figures
    """
    # Needs to be set here so each worker
    # Has the same settings
    sns.set_theme(**seaborn_config)
    logging.info("Plotting and showing %s", data[0])
    fig = plot_function(data[1])
    fig.show()
    plt.close(fig)
    return


def create_4x1_raw_diff_plot(star,
                             mag_max_variation=None,
                             diff_max_variation=None):
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
    if mag_max_variation != None and differential_magnitude_config != None:
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
    day_frames = star.groupby(
        [star["time"].dt.year, star["time"].dt.month, star["time"].dt.day])
    days = len(day_frames)
    star_name = star["id"].unique()[0]
    fig, axes = plt.subplots(nrows=4,
                             ncols=days,
                             figsize=(5 * days, 15),
                             sharex=False)
    if days == 1:
        axes = np.array(axes)
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
                          y=frame["mag"],
                          error=frame["error"],
                          axes=day_ax[:2],
                          yrange=mag_lim,
                          **magnitude_config)
        # Differential Magnitude
        plot_line_scatter(x=frame["time"],
                          y=frame["average_diff_mags"],
                          error=frame["average_uncertainties"],
                          axes=day_ax[2:],
                          yrange=diff_lim,
                          **differential_magnitude_config)
        day_ax[0].set_title(str(day))

        # end day loop
    if days > 1:
        for col in axes:
            col[0].get_shared_x_axes().join(*col)
        for row in axes.transpose():
            row[0].get_shared_y_axes().join(*row)
        for ax in axes.flat:
            ax.label_outer()
    else:
        axes[0].get_shared_x_axes().join(*axes)

        fig.subplots_adjust(wspace=0.025)
    fig.suptitle(("Raw and differential magnitude of star " + star_name))
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig


def plot_line_scatter(x,
                      y,
                      ylabel,
                      xlabel,
                      error,
                      axes,
                      color="blue",
                      yrange=None):
    """Creates Two plots with inputted axes, one scatter and one line.
    The scatter plot is made with errorbars, the line plot is made with fill between
    error.

    Parameters
    ----------
    x : List[Number] or List[Time]
        Numerical x-data.
    y : List[Number]
        Numerical y-data
    ylabel : str
        Label of the y-axis
    xlabel : str
        Label of the x-axis
    error : List[Number]
        Error of the y-data
    axes : axes
        Axis objects to plot in
    color : str, optional
        Colour information for plots, by default "blue"
    yrange : Tuple(Number, Number), optional
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
        **fill_error_config
    }
    error_settings = {"x": x, **bar_error_config}

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
