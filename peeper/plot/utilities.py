from os import PathLike
from typing import Dict, Tuple
import logging
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates

import numpy as np


class Singleton:
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


class WorkerFigure(Singleton):
    def __init__(
        self,
        nrows: int,
        ncols: int,
        figsize: Tuple[int, int],
        name: str,
        plot_config: Dict,
        output_folder: PathLike,
    ):
        plt.ioff()

        self.plot_config = plot_config
        self.nrows = nrows
        self.ncols = ncols
        self.figsize = figsize
        self.name = name
        self.set_axes()
        self.output_folder = output_folder
        if self.axes.ndim == 1:
            self.single_day = True
        else:
            self.single_day = False

    def set_axes(self):
        sns.set_theme(**self.plot_config["seaborn"])
        self.fig, self.axes = plt.subplots(
            num=self.name,
            clear=True,
            tight_layout=True,
            figsize=self.figsize,
            nrows=self.nrows,
            ncols=self.ncols,
            sharex=False,
        )
        self.axes = np.asanyarray(self.axes).transpose()
        self.axis_index = 0

    def get_next_axis(self):
        if self.single_day:
            self.current_axis = self.axes
            return self.current_axis
        else:
            if self.axis_index >= (self.axes.shape[0] - 1):
                return self.axes[self.axis_index]
            else:
                self.current_axis = self.axes[self.axis_index]
                self.axis_index += 1
                return self.current_axis

    def reset_figure(self):
        self.set_axes()

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

    def save(self, file_name: str):
        """Generates output path, calls plotting function then saves figure to specified file"""
        if not self.output_folder.exists():
            logging.info("Creating directory %s", self.output_folder)
            self.output_folder.mkdir(parents=True, exist_ok=True)
        output_file = self.output_folder.joinpath(file_name + ".png")
        self.fig.subplots_adjust(wspace=0.025)
        self.fig.autofmt_xdate()
        self.fig.savefig(fname=output_file, transparent=False, bbox_inches="tight")

    def set_super_title(self, name):
        self.fig.suptitle("Raw and differential magnitude of star " + name)
