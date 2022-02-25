from attrs import define, field
from seaborn.axisgrid import FacetGrid
from shutterbug.data.graphing.builder import BuilderBase
from typing import Tuple, Iterable, Optional
from shutterbug.data.interfaces.internal import Graph
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sns.set_theme(style="darkgrid", context="paper")


@define(slots=True)
class SeabornGraph(Graph):
    _sns_graph: FacetGrid = field()

    """Seaborn graph wrapper"""

    def render(self):
        pass


@define(slots=True)
class SeabornBuilder(BuilderBase):
    """Builder for Seaborn-based graphs"""

    _plot: FacetGrid = field(init=False)

    def build(self) -> SeabornGraph:
        """Builds a Seaborn graph from input settings.
        Requires data to be added before building.

        :returns: SeabornGraph, a wrapper for the underlying graph

        """

        if self._data.empty:
            raise ValueError("Unable to build graph, no data has been given to builder")
        if not self._size[1] == None and not self._size[0] == None:
            aspect = self._size[0] / self._size[1]
        else:
            aspect = None
        self._plot = sns.FacetGrid(
            self._data,
            col="date",
            sharey=True,
            xlim=self._axis_limits[0],
            ylim=self._axis_limits[1],
            height=self._size[1],
            aspect=aspect,
        )
        self._plot.map(self._graph, "data", "error")
        (
            self._plot.map(plt.axhline)
            .set_axis_labels(*self._axis_names)
            .set_titles("{col_name}")
            .tight_layout(w_pad=0.25)
        )
        self._plot.figure.title = self._title
        return SeabornGraph(_sns_graph=self._plot)

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
        x = data.index.array
        y = data.to_numpy()
        if self._type == "scatter":
            plt.scatter(x, y, **kwargs)
        elif self._type == "line":
            plt.scatter(x, y, **kwargs)
        if error is not None:
            axes = plt.gca()
            err = error.to_numpy()
            if self._error_display == "bar":
                axes.errorbar(y=y, x=x, yerr=err, label="Error", color="black")
            if self._error_display == "fill":
                e_pos, e_neg = self._calc_error(data=y, error=err)
                axes.fill_between(x=x, y1=e_pos, y2=e_neg, **kwargs)
            axes.legend()
