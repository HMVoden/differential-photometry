import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Callable

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import toml

import differential_photometry.math_utils as math
import differential_photometry.stats as stats
import differential_photometry.utilities as util

# Get config information
plot_config = toml.load("config/plotting.toml")
seaborn_config = plot_config["seaborn"]
magnitude_config = plot_config["magnitude"]
differential_magnitude_config = plot_config["differential_magnitude"]
bar_error_config = plot_config["error"]["bar"]
fill_error_config = plot_config["error"]["fill"]


def plot_and_save_all(df: pd.DataFrame,
                      uniform_y_axis: bool = False,
                      split: bool = False):
    to_plot = []
    if uniform_y_axis is True:
        columns = ["mag", "average_diff_mags"]
        max_variation = math.timeseries_largest_range(
            **util.arrange_time_star(df, columns))
        mag_max_variation = max_variation["mag"] / 2
        diff_max_variation = max_variation["average_diff_mags"] / 2

        # Divide by 2 to keep most data in viewing range as
        # this encompasses the entire range (half above, half below)
        logging.debug("Maximum raw magnitude variation is: %s",
                      mag_max_variation)
        logging.debug("Maximum differential magnitude variation is: %s",
                      diff_max_variation)
    else:
        mag_max_variation = None
        diff_max_variation = None
    if split is True:
        non_varying, varying = util.split_on(df, "varying")
        to_plot.append(non_varying)
        to_plot.append(varying)
    else:
        to_plot.append(df)
    #end ifs
    for frame in to_plot:
        star_frames = frame.groupby("name", sort=False)
        raw_diff_magnitudes(star_frames,
                            mag_max_variation=mag_max_variation,
                            diff_max_variation=diff_max_variation,
                            save=True)


def raw_diff_magnitudes(star_frames: pd.DataFrame,
                        mag_max_variation: float = None,
                        diff_max_variation: float = None,
                        save: bool = False):
    mpl = mp.log_to_stderr()

    mpl.setLevel(logging.DEBUG)
    # Save or return
    # Mulitprocess to speed up awful plotting code
    with ProcessPoolExecutor(max_workers=4) as executor:

        if save is True:
            plot_function = partial(
                create_4x1_raw_diff_plot,
                mag_max_variation=mag_max_variation,
                diff_max_variation=diff_max_variation,
            )
            saving_function = partial(save_plots, plot_function=plot_function)
            # for name, frame in star_frames:
            #     saving_function([name, frame])
            list(executor.map(saving_function, star_frames, chunksize=16))
        else:
            # for group in star_frames:
            #     show_plots(group)
            # list(map(show_plots, star_frames))
            list(executor.map(show_plots, star_frames, chunksize=16))
        # pass


def save_plots(data: pd.DataFrame, plot_function):
    # Needs to be set here so each worker
    # Has the same settings
    sns.set_theme(**seaborn_config)
    logging.info("Plotting and saving %s", data[0])
    output_file = generate_output_path(data[1])
    if not output_file.exists():
        logging.info("Creating directory %s", output_file)
        output_file.mkdir(parents=True, exist_ok=True)
    output_file = output_file.joinpath(data[0] + ".png")
    logging.debug("Output file: %s", output_file)
    fig = plot_function(data[1])
    fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")
    plt.close(fig)
    return


def generate_output_path(data: pd.DataFrame) -> PathLike:
    columns = data.columns
    output_path = Path.cwd()  # current directory of script
    dataset = Path(toml.load("config/working.toml")["current_file"])
    target_cluster = dataset.stem.split("_")[0]
    output_path = output_path.joinpath(*plot_config['output']['base'].values())
    output_path = output_path.joinpath(target_cluster)  # Target of interest
    output_path = output_path.joinpath(dataset.stem)  # Filename loaded in
    if "corrected" in columns:
        output_path = output_path.joinpath(
            *plot_config['output']['corrected'].values())
    if data["varying"].any() == True:
        output_path = output_path.joinpath(
            *plot_config['output']['varying'].values())
    else:
        output_path = output_path.joinpath(
            *plot_config['output']['non_varying'].values())
    return output_path


def show_plots(data, plot_function):
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
    if mag_max_variation != None and differential_magnitude_config != None:
        mag_mean = np.average(star["mag"], weights=(1 / star["error"]**2))
        diff_mean = np.average(star["average_diff_mags"],
                               weights=(1 / star["average_uncertainties"]**2))
        mag_lim = (mag_mean - mag_max_variation, mag_mean + mag_max_variation)
        diff_lim = (diff_mean - diff_max_variation,
                    diff_mean + diff_max_variation)
    else:
        mag_lim = None
        diff_lim = None
    #end if
    day_frames = star.groupby("d_m_y")
    days = len(day_frames)
    star_name = star["name"].unique()[0]
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
    fig.suptitle(("Raw and differential magntitude of star " + star_name))
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
