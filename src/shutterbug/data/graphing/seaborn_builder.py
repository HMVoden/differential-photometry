from attrs import define, field
from seaborn.axisgrid import FacetGrid
from shutterbug.data.graphing.builder import BuilderBase
from typing import Sequence, Tuple
from shutterbug.data.interfaces.internal import GraphInterface
import seaborn as sns
import matplotlib.pyplot as plt


@define(slots=True)
class SeabornGraph(GraphInterface):
    _sns_graph: FacetGrid = field()

    """Seaborn graph wrapper"""

    def render(self):
        pass


@define(slots=True)
class SeabornBuilder(BuilderBase):
    """Builder for Seaborn-based graphs"""

    _plot: FacetGrid = field(init=False)

    def build(self) -> SeabornGraph:
        if self._data.empty:
            raise ValueError("Unable to build graph, no data has been given to builder")
        relplot_settings = {
            "data": self._data,
            "y": "data",
            "x": "time",
            "col": "date",
            "kind": self.type,
            "height": self.size[0],
            "estimator": None,
            "facet_kws": {
                "sharey": True,
                "xlim": self._axis_limits[0],
                "ylim": self._axis_limits[1],
            },
        }
        self._plot = sns.relplot(**relplot_settings)
        (
            self._plot.map(plt.axhline)
            .set_axis_labels(*self._axis_names)
            .set_titles("Date: {col_name}")
            .tight_layout(w_pad=0.25)
        )
        self._plot.figure.title = self._title

    def _add_error(self):
        if self._error_display == "bar":
            self._add_bar_error()
        elif self._error_display == "fill":
            self._add_fill_error()

    def _calc_error_size(self) -> Tuple[Sequence[float], Sequence[float]]:
        data = self._data["data"].to_numpy()
        error = self._data["error"].to_numpy()
        error_plus = data + error
        error_neg = data - error
        return error_plus, error_neg

    def _add_bar_error(self):
        self._plot.map(plt.errorbar)

    def _add_fill_error(self):
        pass
