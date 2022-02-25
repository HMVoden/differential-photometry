from attr import field, define
from shutterbug.data.interfaces.internal import Graph

from shutterbug.data.interfaces.external import GraphBuilder
from shutterbug.data.star import Star


@define(slots=True)
class GraphDirector:
    """Takes a graph builder and is then used to construct all graphs via this
    builder"""

    builder: GraphBuilder = field()

    def build_graph(self, data: Star) -> Graph:
        """Builds and returns a graph from specified data"""
        pass
