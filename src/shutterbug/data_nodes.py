from __future__ import annotations
from abc import abstractmethod
from shutterbug.data import Dataset
from shutterbug.data.interfaces.internal import Graph, Writer
from shutterbug.data.interfaces.external import GraphBuilder, Loader
from shutterbug.interfaces.external import ControlNode
from attr import field, define
from typing import Generator
from pathlib import Path


@define
class DatasetNode(ControlNode):
    @abstractmethod
    def execute(self) -> Generator[Dataset, None, None]:
        raise NotImplementedError


@define
class StoreNode(ControlNode):
    source: Loader = field()
    writer: Writer = field()

    def execute(self) -> None:
        for star in self.source:
            self.writer.write(star)


@define
class FilesystemSave:
    output_location: Path = field()


@define
class GraphSaveNode(DatasetNode, FilesystemSave):
    datasets: DatasetNode = field()
    graph_builder: GraphBuilder = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass


@define
class CSVSaveNode(DatasetNode, FilesystemSave):
    datasets: DatasetNode = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass
