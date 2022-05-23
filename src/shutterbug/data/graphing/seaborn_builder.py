from pathlib import Path
from typing import Iterable, Optional, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from attrs import define, field
from seaborn.axisgrid import FacetGrid
from shutterbug.data.graphing.builder import BuilderBase
from shutterbug.data.interfaces.internal import Graph

sns.set_theme(style="darkgrid", context="paper")


@define(slots=True)
class SeabornGraph(Graph):
    sns_graph: FacetGrid = field()

    """Seaborn graph wrapper"""

    def render(self):
        pass

    def save(self, filename: Path) -> None:
        self.sns_graph.savefig(filename)
        plt.close()


@define(slots=True)
class SeabornBuilder(BuilderBase):
    """Builder for Seaborn-based graphs"""

    _plot: FacetGrid = field(init=False)

    def build(self) -> SeabornGraph:
        """Builds a Seaborn graph from input settings.
        Requires data to be added before building.

        :returns: SeabornGraph, a wrapper for the underlying graph

        """

        if self.data.empty:
            raise ValueError("Unable to build graph, no data has been given to builder")
        if not self.size[1] == None and not self.size[0] == None:
            aspect = self.size[0] / self.size[1]
        else:
            aspect = 3
        data = self.data.rename("data")
        data = pd.merge(left=data, right=self.error.rename("error"), on="time")
        data["date"] = data.index.date
        ylims = self._calc_ylim_from_data(data["data"], y_limit=self.axis_limits[1])
        self._plot = sns.FacetGrid(
            data,
            col="date",
            aspect=aspect,
            height=self.size[1],
            sharey=True,
            sharex=False,
            legend_out=True,
            ylim=ylims,
        )
        self._plot.map(self._graph, "data", "error").set_axis_labels(
            *self.axis_names
        ).set_titles("{col_name}").tight_layout(w_pad=0.25)
        self._plot.fig.suptitle(self.title)
        self._plot.fig.subplots_adjust(top=0.85)
        for ax in self._plot.axes.flatten():
            cur_title = ax.title.get_text()
            ax.set_title(
                f"{cur_title} \n IVN: {self.features[cur_title]['Inverse Von Neumann']:.2f}, IQR: {self.features[cur_title]['IQR']:.2f}"
            )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        self._plot.fig.autofmt_xdate()
        return SeabornGraph(sns_graph=self._plot)

    @staticmethod
    def _calc_ylim_from_data(
        data: Iterable[float], y_limit: Optional[float] = None
    ) -> Tuple[float, float]:
        if y_limit is None:
            y_limit = 1
        data = np.asarray(data).flatten()
        med = np.median(data)
        return (med - y_limit, med + y_limit)

    @staticmethod
    def _calc_error(
        data: Iterable[float], error: Iterable[float]
    ) -> Tuple[Iterable[float], Iterable[float]]:
        """Calculates the error spread above and below the data points"""
        data = np.asarray(data).flatten()
        error = np.asarray(error).flatten()
        error_plus = data + error
        error_neg = data - error
        return error_plus, error_neg  # type: ignore

    def _graph(self, data: pd.Series, error: Optional[pd.Series] = None, **kwargs):
        """Generates Seaborn graph from map function"""
        x = data.index
        y = data
        if self.type == "scatter":
            plt.scatter(
                x=x,
                y=y,
                **kwargs,
            )
        elif self.type == "line":
            plt.plot(x, y, **kwargs)
        if error is not None:
            err = error
            if self.error_display == "bar":
                plt.errorbar(
                    y=y, x=x, yerr=error, label="Error", color="black", fmt="none"
                )
            if self.error_display == "fill":
                e_pos, e_neg = self._calc_error(data=y, error=err)
                plt.fill_between(x=x, y1=e_pos, y2=e_neg, **kwargs)
        plt.legend()
