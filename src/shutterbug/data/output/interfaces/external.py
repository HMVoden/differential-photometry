from typing import Iterable, Protocol

from shutterbug.output.interfaces.internal import GraphInterface


class GraphFactoryInterface(Protocol):
    def make(
        self,
        title: str,
        x: Iterable[str],
        y: Iterable[str],
        x_axis_name: str,
        y_axis_name: str,
    ) -> GraphInterface:
        ...
