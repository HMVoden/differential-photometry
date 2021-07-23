import matplotlib

matplotlib.use("Agg")
import gc
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path
from typing import Dict, List, Tuple

import config.manager as config
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shutterbug.data.input_output as io
import shutterbug.data.utilities as data_util
import shutterbug.plot.utilities as plot_util
import shutterbug.progress_bars as bars
import seaborn as sns
from pandas.core.groupby.generic import DataFrameGroupBy

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

    df.groupby(["inter_varying", "graph_intra"]).pipe(
        generate_data_folders, uniform_y_axis=uniform_y_axis, correct=correct
    ).pipe(
        multiprocess_save,
        correct=correct,
        mag_max_variation=mag_max_variation,
        diff_max_variation=diff_max_variation,
        plot_config=plot_config,
    )


def generate_data_folders(
    group: DataFrameGroupBy, uniform_y_axis: bool, correct: bool
) -> List[Tuple[pd.DataFrame, Path]]:
    for inter, intra in group.groups:
        folder = io.generate_graph_output_path(
            corrected=correct,
            uniform=uniform_y_axis,
            inter_varying=inter,
            intra_varying=intra,
        )
        group.groups[(inter, intra)].output_folder = folder
    return group


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
            **data_util.arrange_time_star(df, columns)
        )

        # Divide by 2 to keep most data in viewing range as
        # this encompasses the entire range (half above, half below)
        mag_max_variation = np.round(max_variation["mag"] / 2, decimals=1)
        diff_max_variation = np.round(
            max_variation["average_diff_mags"] / 2, decimals=1
        )
    logging.info("Magnitude y-axis range is: %s", mag_max_variation)
    logging.info("Differential y-axis range is: %s", diff_max_variation)
    return mag_max_variation, diff_max_variation


def multiprocess_save(
    star_frames: pd.DataFrame,
    plot_config: Dict,
    correct: bool,
    mag_max_variation: float = None,
    diff_max_variation: float = None,
):
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
    global frames  # Shares for threads
    # Mulitprocess to speed up awful plotting code
    pbar_folders = bars.get_progress_bar(
        name="folders",
        total=len(star_frames),
        desc="Plotting folders",
        unit="folders",
        color="blue",
        leave=False,
    )
    for (name), group in star_frames:
        output_folder = star_frames.groups[name].output_folder
        bars.status.update(stage="Plotting and saving stars")
        pbar = bars.get_progress_bar(
            name="plot_and_save",
            total=group.id.nunique(),
            desc="  Plotting and saving stars",
            unit="stars",
            color="magenta",
            leave=False,
        )
        pbar.refresh()
        logging.info("Writing to folder %s", output_folder)

        group["id"] = group.id.cat.remove_unused_categories().cat.as_ordered()

        # for _, stars in group.groupby("id"):
        #     build_and_save_figure(
        #         df=stars,
        #         plot_config=plot_config,
        #         correct=correct,
        #         output_folder=output_folder,
        #         mag_max_variation=mag_max_variation,
        #         diff_max_variation=diff_max_variation,
        #     )
        #     pbar.update()

        with ProcessPoolExecutor(max_workers=(cpu_count() - 1)) as executor:
            futures = {
                executor.submit(
                    build_and_save_figure,
                    df=stars,
                    plot_config=plot_config,
                    correct=correct,
                    output_folder=output_folder,
                    mag_max_variation=mag_max_variation,
                    diff_max_variation=diff_max_variation,
                )
                for _, stars in group.groupby("id")
            }
            for future in as_completed(futures):
                pbar.update()
        pbar_folders.update()
        gc.collect()


def build_and_save_figure(
    df: pd.DataFrame,
    output_folder: Path,
    plot_config: Dict,
    correct: bool = False,
    mag_max_variation: float = None,
    diff_max_variation: float = None,
) -> bool:
    mag_y = "mag"
    diff_y = "average_diff_mags"
    if correct is True:
        mag_y = "c_" + mag_y
        diff_y = "c_" + diff_y

    mag_lim = limits_from_median(df[mag_y], mag_max_variation)
    diff_lim = limits_from_median(df[diff_y], diff_max_variation)

    # Needs to be set here so each worker
    # Has the same settings
    figure = plot_util.WorkerFigure(
        nrows=4,
        ncols=df.y_m_d.nunique(),
        figsize=(5 * df.y_m_d.nunique(), 15),
        name="fig1",
        output_folder=output_folder,
        plot_config=plot_config,
    )

    df.groupby("y_m_d").apply(
        create_4x1_raw_diff_plot,
        figure=figure,
        correct=correct,
        plot_config=plot_config,
        mag_lim=mag_lim,
        diff_lim=diff_lim,
    )
    figure.share_columns_x()
    figure.share_rows_y()
    figure.set_label_outer()
    figure.set_date_formatter()
    figure.set_super_title(df["id"].unique()[0])
    figure.save(df["id"].unique()[0])
    figure.reset_figure()
    return df  # placeholder


def limits_from_median(
    ydata: List[float], max_variation: float = None
) -> Tuple[float, float]:
    if max_variation is None:
        return None
    median = np.median(ydata)
    return (median - max_variation, median + max_variation)


def create_4x1_raw_diff_plot(
    df: pd.DataFrame,
    figure: plot_util.WorkerFigure,
    correct: bool,
    plot_config: Dict,
    mag_lim: float = None,
    diff_lim: float = None,
) -> pd.DataFrame:
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

    mag_y = "mag"
    diff_y = "average_diff_mags"
    if correct is True:
        mag_y = "c_" + mag_y
        diff_y = "c_" + diff_y

    axes = figure.get_next_axis()

    # Raw Magnitude
    plot_line_scatter(
        x=df["time"],
        y=df[mag_y],
        ylabel=plot_config["magnitude"]["ylabel"],
        xlabel=plot_config["magnitude"]["xlabel"],
        color=plot_config["magnitude"]["color"],
        error=df["error"],
        axes=axes[:2],
        yrange=mag_lim,
        plot_config=plot_config,
    )
    # Differential Magnitude
    plot_line_scatter(
        x=df["time"],
        y=df[diff_y],
        ylabel=plot_config["differential_magnitude"]["ylabel"],
        xlabel=plot_config["differential_magnitude"]["xlabel"],
        color=plot_config["differential_magnitude"]["color"],
        error=df["average_uncertainties"],
        axes=axes[2:],
        yrange=diff_lim,
        plot_config=plot_config,
    )
    figure.set_current_column_title(df.name)
    return df  # If you want to pipe this


def plot_line_scatter(
    x: List[float],
    y: List[float],
    ylabel: str,
    xlabel: str,
    error: List[float],
    axes: List[plt.Axes],
    plot_config: Dict,
    color: str = "blue",
    yrange: Tuple[float, float] = None,
):
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
        "y1": error_plus.values,
        "y2": error_neg.values,
        "color": color,
        **plot_config["error"]["fill"],
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
