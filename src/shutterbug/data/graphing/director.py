from attr import field, define
from shutterbug.data.graphing.graph import Graph

from shutterbug.data.interfaces.external import GraphBuilder


@define
class GraphDirector:
    """Takes a graph builder and is then used to construct all graphs via this
    builder"""

    builder: GraphBuilder = field()

    def build_graph(self, data) -> Graph:
        """Builds and returns a graph from specified data"""
        pass
