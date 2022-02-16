from attr import field, define
from shutterbug.data.interfaces.internal import GraphInterface

from shutterbug.data.interfaces.external import GraphBuilderInterface
from shutterbug.data.star import Star


@define(slots=True)
class GraphDirector:
    """Takes a graph builder and is then used to construct all graphs via this
    builder"""

    builder: GraphBuilderInterface = field()

    def build_graph(self, data: Star) -> GraphInterface:
        """Builds and returns a graph from specified data"""
        pass
