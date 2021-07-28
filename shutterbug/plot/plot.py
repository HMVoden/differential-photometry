import matplotlib

matplotlib.use("Agg")
import gc
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import shutterbug.data.input_output as io
import shutterbug.plot.utilities as plot_util
import shutterbug.progress_bars as bars
import seaborn as sns

manager = None
status = None


def plot_and_save_all(
    ds: xr.Dataset, plot_config: Dict, uniform_y_axis: bool, offset: bool
):
    # np.array(np.meshgrid([True, False], [True, False])).reshape((-1,2))
    logging.info("Starting graphing...")
    ds = ds.swap_dims({"star": "intra_varying"})
    ds = ds.set_index(varying=("intra_varying", "inter_varying"))

    ds.groupby("varying").map(
        multiprocess_save,
        offset=offset,
        uniform=uniform_y_axis,
        plot_config=plot_config,
    )

    logging.info("Finished graphing")
    return ds.reset_index("varying")


def generate_data_folders(
    ds: xr.Dataset, uniform_y_axis: bool, offset: bool
) -> List[Tuple[pd.DataFrame, Path]]:
    intra, inter = np.unique(ds["varying"])[0]
    ds.attrs["output_folder"] = io.generate_graph_output_path(
        offset=offset,
        uniform=uniform_y_axis,
        intra_varying=intra,
        inter_varying=inter,
    )
    return ds


def setup_plot_dataset(ds: xr.Dataset, offset: bool, uniform: bool) -> xr.Dataset:
    ds = ds.pipe(generate_data_folders, uniform_y_axis=uniform, offset=offset)
    ds = ds.reset_index("varying").swap_dims({"varying": "star"})
    if offset == True:
        ds["mag"] = ds["mag"].groupby("time.date") - ds["mag_offset"]
        ds["average_diff_mags"] = (
            ds["average_diff_mags"].groupby("time.date") - ds["dmag_offset"]
        )
    if uniform == True:
        pass  # do something here

    # ds = ds.stack(time_stack={"time", "time.date"})
    return ds


def teardown_plot_dataset(ds: xr.Dataset) -> xr.Dataset:
    # ds = ds.unstack("time_stack")
    # ds = ds.drop_dims("time.date", errors="ignore")
    return ds


def multiprocess_save(
    ds: xr.Dataset,
    plot_config: Dict,
    uniform: bool,
    offset: bool,
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
    global frame  # Shares for threads
    # Mulitprocess to speed up awful plotting code
    # pbar_folders = bars.get_progress_bar(
    #     name="folders",
    #     total=len(star_frames),
    #     desc="Plotting folders",
    #     unit="folders",
    #     color="blue",
    #     leave=False,
    # )
    frame = setup_plot_dataset(ds, offset, uniform)
    bars.status.update(stage="Plotting and saving stars")
    pbar = bars.start(
        name="plot_and_save",
        total=frame["star"].size,
        desc="  Plotting and saving stars",
        unit="stars",
        color="magenta",
        leave=False,
    )
    logging.info("Writing to folder %s", ds.attrs["output_folder"])
    # for _, stars in frame.groupby("star"):
    #     build_and_save_figure(
    #         ds=stars,
    #         plot_config=plot_config,
    #     )
    #     pbar.update()

    with ProcessPoolExecutor(max_workers=(cpu_count() - 1)) as executor:
        futures = {
            executor.submit(
                build_and_save_figure,
                ds=stars,
                plot_config=plot_config,
            )
            for _, stars in frame.groupby("star")
        }
        for future in as_completed(futures):
            pbar.update()
            try:
                future.result()
            except Exception as e:
                print("%s generated error: %s", future, e)
    # pbar_folders.update()
    frame = teardown_plot_dataset(frame)
    gc.collect()

    return frame


def build_and_save_figure(
    ds: xr.Dataset,
    plot_config: Dict,
) -> bool:

    mag_lim = limits_from_median(ds["mag"], ds.attrs["mag_var"])
    diff_lim = limits_from_median(ds["average_diff_mags"], ds.attrs["diff_var"])

    # Needs to be set here so each worker
    # Has the same settings
    figure = plot_util.WorkerFigure(
        nrows=4,
        ncols=len(np.unique(ds["time.date"])),
        figsize=(5 * len(np.unique(ds["time.date"])), 15),
        name="fig1",
        output_folder=ds.attrs["output_folder"],
        plot_config=plot_config,
    )

    ds.groupby("time.date").map(
        create_4x1_raw_diff_plot,
        figure=figure,
        plot_config=plot_config,
        mag_lim=mag_lim,
        diff_lim=diff_lim,
    )

    figure.share_columns_x()
    figure.share_rows_y()
    figure.set_label_outer()
    figure.set_date_formatter()
    figure.set_super_title(str(ds["star"].data))
    figure.save(str(ds["star"].data))
    figure.reset_figure()
    return ds  # placeholder


def limits_from_median(
    ydata: List[float], max_variation: float = None
) -> Tuple[float, float]:
    if max_variation is None:
        return None
    median = np.median(ydata)
    return (median - max_variation, median + max_variation)


def create_4x1_raw_diff_plot(
    ds: xr.Dataset,
    figure: plot_util.WorkerFigure,
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
    axes = figure.get_next_axis()

    # Raw Magnitude
    plot_line_scatter(
        x=ds["time"].values,
        y=ds["mag"].values,
        ylabel=plot_config["magnitude"]["ylabel"],
        xlabel=plot_config["magnitude"]["xlabel"],
        color=plot_config["magnitude"]["color"],
        error=ds["error"].values,
        axes=axes[:2],
        yrange=mag_lim,
        plot_config=plot_config,
    )
    # Differential Magnitude
    plot_line_scatter(
        x=ds["time"].values,
        y=ds["average_diff_mags"].values,
        ylabel=plot_config["differential_magnitude"]["ylabel"],
        xlabel=plot_config["differential_magnitude"]["xlabel"],
        color=plot_config["differential_magnitude"]["color"],
        error=ds["average_uncertainties"].values,
        axes=axes[2:],
        yrange=diff_lim,
        plot_config=plot_config,
    )
    figure.set_current_column_title(str(np.unique(ds["time.date"])[0]))
    return ds


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
        "y1": error_plus,
        "y2": error_neg,
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
