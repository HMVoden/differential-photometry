import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns


class WorkerFigure:
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
            title += f"\n Augmented Dickey-Fuller value: {test_statistic:.2f}, varying when p-value: >=0.05"
        self.fig.suptitle(title)
