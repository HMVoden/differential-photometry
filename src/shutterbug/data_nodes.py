from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Generator

from attr import define, field

from shutterbug.data import BuilderBase, Dataset
from shutterbug.data.interfaces.external import Loader
from shutterbug.data.interfaces.internal import Graph, Writer
from shutterbug.interfaces.external import ControlNode


@define
class DatasetNode(ControlNode):
    datasets: DatasetNode = field()

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
    only_variable: bool = field()


@define
class GraphSaveNode(DatasetNode, FilesystemSave):
    graph_builder: BuilderBase = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass


@define
class CSVSaveNode(DatasetNode, FilesystemSave):
    def execute(self) -> Generator[Dataset, None, None]:
        pass
