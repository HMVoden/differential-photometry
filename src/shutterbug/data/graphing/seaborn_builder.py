from attrs import define
from shutterbug.data.graphing.builder import BuilderBase
import pandas as pd

from shutterbug.data.interfaces.internal import GraphInterface
import seaborn as sns


@define(slots=True)
class SeabornGraph(GraphInterface):
    """Seaborn graph wrapper"""

    def render(self):
        pass


@define(slots=True)
class SeabornBuilder(BuilderBase):
    """Builder for Seaborn-based graphs"""

    def build(self) -> SeabornGraph:
        if self._data.empty:
            raise ValueError("Unable to build graph, no data has been given to builder")
