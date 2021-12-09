import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg, RendererAgg
from matplotlib.figure import Figure
from matplotlib.transforms import BboxBase


class Singleton:
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


# TODO refactor this so it's not so abhorrent
class WorkerFigure(Singleton):
    nrows: int
    ncols: int
    figsize: Tuple[int, int]
    name: str = "worker"
    plot_config: Dict
    output_folder: Path
    axes: npt.NDArray
    _bg: BboxBase
    _renderer: RendererAgg
    canvas: FigureCanvasAgg
    fig: Figure

    def __init__(
        self,
        nrows: int,
        ncols: int,
        figsize: Tuple[int, int],
        plot_config: Dict,
        output_folder: Path,
    ):
        plt.ioff()
        self.plot_config = plot_config
        sns.set_theme(**self.plot_config["seaborn"])
        self.nrows = nrows
        self.ncols = ncols
        self.figsize = figsize
        self.fig, self.axes = plt.subplots(
            num=self.name,
            clear=True,
            tight_layout=True,
            figsize=self.figsize,
            nrows=self.nrows,
            ncols=self.ncols,
            sharex=False,
        )
        self.fig.subplots_adjust(wspace=0.025)
        self.axes = np.asanyarray(self.axes).transpose()
        self.canvas = self.fig.canvas
        self.cid = self.canvas.mpl_connect("draw_event", self.on_draw)

        self.output_folder = output_folder
        if self.axes.ndim == 1:
            self.single_day = True
        else:
            self.single_day = False
        self.axis_index = 0
        for ax in self.axes.flatten():
            ax.set_animated(True)
        self.canvas.draw()

    def on_draw(self, event):
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._renderer = cv.get_renderer()
        self._draw_plots()

    def update(self):
        cv = self.canvas
        fig = cv.figure
        if self._bg is None:
            self.on_draw(None)
        else:
            cv.restore_region(self._bg)
            self._draw_plots
            cv.blit(fig.bbox)
        cv.flush_events()

    def get_next_axis(self):
        if self.single_day:
            self.current_axis = self.axes
            return self.current_axis
        else:
            if self.axis_index >= (self.axes.shape[0]):
                return self.axes[self.axis_index]
            else:
                self.current_axis = self.axes[self.axis_index]
                self.axis_index += 1
                return self.current_axis

    def share_rows_y(self):
        if self.single_day:
            return  # do nothing, no work required
        else:
            for row in self.axes.transpose():
                row[0].get_shared_y_axes().join(*row)

    def share_columns_x(self):
        if self.single_day:
            self.axes[0].get_shared_x_axes().join(*self.axes)
        else:
            for col in self.axes:
                col[0].get_shared_x_axes().join(*col)

    def set_current_column_title(self, title: str):
        self.current_axis[0].set_title(title)

    def set_date_formatter(self):
        if self.single_day:
            self.axes[-1].xaxis.set_major_formatter(  # set display of time
                mdates.DateFormatter(**self.plot_config["time"])
            )
        else:
            for ax in self.axes.transpose()[-1]:  # Get last row
                ax.xaxis.set_major_formatter(  # set display of time
                    mdates.DateFormatter(**self.plot_config["time"])
                )

    def set_label_outer(self):
        if self.single_day:
            return  # do nothing
        else:
            for ax in self.axes.flatten():
                ax.label_outer()

    def _draw_plots(self):
        renderer = self._renderer
        for ax in self.axes.flatten():
            ax.draw(renderer)

    def save(self, file_name: str):
        self._create_folder()
        output_file = self.output_folder.joinpath(file_name + ".png")
        self.fig.autofmt_xdate()
        self.update()
        self.fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")

    def _create_folder(self):
        if not self.output_folder.exists():
            logging.info("Creating directory %s", self.output_folder)
            self.output_folder.mkdir(parents=True, exist_ok=True)

    def set_super_title(
        self,
        name: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        comparison_stars: Optional[int] = None,
        test_statistic: Optional[float] = None,
    ):
        title = f"Raw and differential magnitude of {name}"
        if x is not None and y is not None:
            title += f"\n X: {x}  Y: {y}"
        if comparison_stars is not None:
            title += f"\n Comparison stars used: {comparison_stars}"
        if test_statistic is not None:
            title += (
                f"\n DDSquare value: {test_statistic:.4f}, varying when value: >=0.01"
            )
        self.fig.suptitle(title)


def max_variation(
    ds: pd.DataFrame,
    uniform_y_axis: bool = False,
    mag_y_scale: float = None,
    diff_y_scale: float = None,
) -> pd.DataFrame:
    if mag_y_scale is not None or diff_y_scale is not None:
        ds.attrs["mag_var"] = mag_y_scale
        ds.attrs["diff_var"] = diff_y_scale
        if mag_y_scale is None or diff_y_scale is None:
            logging.warning(
                "The magnitude or differential magnitude plotting scale is not set."
            )
            logging.warning("Continuing with defaults for unset scale.")

    if uniform_y_axis is True:
        # Calculate the largest deviation along the y-axis
        # for the entire dataset

        ds["mag_var"] = get_largest_range((ds["mag"] - ds["mag_offset"]).values)
        ds["diff_var"] = get_largest_range(
            (ds["average_diff_mags"] - ds["dmag_offset"]).values
        )
    if all(lim in ds.attrs.keys() for lim in ["mag_var", "diff_var"]):
        logging.info("Magnitude y-axis range is: +/- %s", ds["mag_var"].values[0])
        logging.info("Differential y-axis range is: +/- %s", ds["diff_var"].values[0])
    return ds


def get_largest_range(data: List[float]) -> float:
    """Finds the largest range in one part of a timeseries dataset, for example
    if you have three days of timeseries, this will find the largest range that
    can be found in a single day

    Returns
    -------
    Dict
        Dictionary of the data name passed in and the entire dataset of values as the
        dictionary value.

    Returns
    -------
    Dict
        Dictionary of the data name and the largest range for the entire dataset
    """
    # max_variation = np.abs(np.ptp(d))
    ptp = np.ptp(data, axis=0)
    max_variation = np.max(np.abs(ptp))
    max_variation = np.round(max_variation / 2, decimals=1)
    # Divide by 2 to keep most data in viewing range as
    # this encompasses the entire range (half above, half below)
    return max_variation
