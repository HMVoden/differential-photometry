import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import differential_photometry.rao_data as data
import differential_photometry.rao_math as math
import differential_photometry.rao_stats as stats
import differential_photometry.rao_utilities as util


def plot_and_save_all(
    df: pd.DataFrame, *saving, plot_type="magnitude", uniform_y_axis=False
):
    """Takes a pandas dataframe that contains raw magnitude, time as julian date, average magnitude and error, then generates plots for every single star with these values side by side.

    Parameters
    ----------
    dataframe : pd.DataFrame
        A dataframe containing raw magnitude, a time column, average magnitude and errors for magnitudes, with a star's name
    output_filename : str
        the desired filename that will be prepended onto the star's
    """

    if plot_type == "magnitude":
        star_frames = df.groupby("name", sort=False)
        raw_diff_magnitudes(
            star_frames, *saving, uniform_y_axis=uniform_y_axis,
        )


def raw_diff_magnitudes(star_frames, *saving, uniform_y_axis=False):
    if uniform_y_axis == True:
        columns = ["mag", "average_diff_mags"]
        max_variation = math.timeseries_largest_range(
            **util.arrange_time_star(star_frames, columns)
        )

        mag_max_variation = max_variation["mag"] / 3
        diff_max_variation = max_variation["average_diff_mags"] / 3
        # Divide by 3 to keep most data in viewing range
        logging.debug("Maximum raw magnitude variation is: %s", mag_max_variation)
        logging.debug(
            "Maximum differential magnitude variation is: %s", diff_max_variation
        )
    else:
        mag_max_variation = None
        diff_max_variation = None

    mpl = mp.log_to_stderr()
    mpl.setLevel(logging.DEBUG)
    # Save or return
    with ProcessPoolExecutor(max_workers=4) as executor:
        if saving is not None:
            kw = np.array_str(np.arange(0, len(saving)))
            kwargs = dict(zip(kw, saving))
            plot_function = partial(
                create_4x1_raw_diff_plot,
                mag_max_variation=mag_max_variation,
                diff_max_variation=diff_max_variation,
            )
            saving_function = partial(save_plots, plot_function=plot_function, **kwargs)
            # for name, frame in star_frames:
            #     saving_function([name, frame])
            list(executor.map(saving_function, star_frames, chunksize=16))
        else:
            # for group in star_frames:
            #     show_plots(group)
            # list(map(show_plots, star_frames))
            list(executor.map(show_plots, star_frames, chunksize=16))
            # pass


def save_plots(data, plot_function, **saving_settings):
    sns.set_theme(style="darkgrid", context="paper")
    sns.set_palette("deep")
    logging.info("Plotting and saving %s", data[0])
    output_file = Path.cwd()  # current directory
    output_file = output_file.joinpath(*saving_settings.values())
    if not output_file.exists():
        logging.info("Creating directory %s", output_file.parent)
        output_file.mkdir(parents=True)
    output_file = output_file.joinpath(data[0] + ".png")
    logging.info("Output file: %s", output_file)
    fig = plot_function(data[1])
    fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")
    plt.close(fig)
    return


def show_plots(data, plot_function):
    sns.set_theme(style="darkgrid", context="paper")
    sns.set_palette("deep")
    logging.info("Plotting and showing %s", data[0])
    fig = plot_function(data[1])
    fig.show()
    plt.close(fig)
    return


def create_4x1_raw_diff_plot(star, mag_max_variation=None, diff_max_variation=None):
    day_frames = star.groupby("d_m_y")
    days = len(day_frames)
    star_name = star["name"].unique()[0]
    fig, axes = plt.subplots(nrows=4, ncols=days, figsize=(5 * days, 15), sharex=False)
    if days == 1:
        axes = np.array(axes)
    axes = np.asanyarray(axes).transpose()

    for i, frame_dict in enumerate(day_frames):
        frame = frame_dict[1]
        day = frame_dict[0]
        logging.info("Graphing star day %s", day)
        if days > 1:
            day_ax = axes[i]
        else:
            day_ax = axes

        # Raw Magnitude
        plot_line_scatter(
            x=frame["time"],
            y=frame["mag"],
            error=frame["error"],
            xlabel="Julian Date",
            ylabel="Raw Magnitude",
            axes=day_ax[:2],
            color="darkgreen",
            yrange=mag_max_variation,
        )
        # Differential Magnitude
        plot_line_scatter(
            x=frame["time"],
            y=frame["average_diff_mags"],
            error=frame["average_uncertainties"],
            xlabel="Julian Date",
            ylabel="Average Differential Magnitude",
            axes=day_ax[2:],
            color="orange",
            yrange=diff_max_variation,
        )
        day_ax[0].set_title(str(day))

        # end day loop
    if days > 1:
        for col in axes:
            col[0].get_shared_x_axes().join(*col)
        if mag_max_variation is None and diff_max_variation is None:
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


def plot_line_scatter(x, y, ylabel, xlabel, error, axes, color="blue", yrange=None):
    # For the fill between error bars
    error_plus = y + error
    error_neg = y - error

    fill_between = {
        "x": x,
        "y1": error_plus,
        "y2": error_neg,
        "alpha": 0.45,
        "label": "Error",
        "color": color,
    }
    error_settings = {"x": x, "fmt": "none", "color": "black", "capsize": 1}

    sns.lineplot(ax=axes[0], x=x, y=y, ci=None, color=color)
    axes[0].fill_between(**fill_between)
    sns.scatterplot(ax=axes[1], x=x, y=y, ci=None, color=color)
    axes[1].errorbar(y=y, yerr=error, label="Error", **error_settings)
    for ax in axes:
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        if yrange is not None:
            mean = stats.weighted_mean(y, error)
            ax.set_ylim((mean - yrange), (mean + yrange))
