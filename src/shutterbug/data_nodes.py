from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, List, Union

from attr import define, field

from shutterbug.data import BuilderBase, Dataset
from shutterbug.data.interfaces.external import Loader
from shutterbug.data.interfaces.internal import Writer
from shutterbug.interfaces.external import ControlNode


@define
class DatasetNode(ControlNode):
    datasets: Union[DatasetNode, Dataset] = field()

    @abstractmethod
    def execute(self) -> Generator[Dataset, None, None]:
        raise NotImplementedError


@define
class DatasetLeaf(DatasetNode):
    datasets: Dataset

    def execute(self) -> Generator[Dataset, None, None]:
        logging.debug("Handing dataset to nodes")
        yield self.datasets


@define
class StoreNode(ControlNode):
    source: Loader = field()
    writer: Writer = field()

    def execute(self) -> None:
        logging.debug("Storing dataset")
        stars = []
        for star in self.source:
            stars.append(star)
            if len(stars) >= 50:
                self.writer.write(stars)
                stars = []

        self.writer.write(stars)


@define
class GraphSaveNode(DatasetNode):
    graph_builder: BuilderBase = field()
    output_location: Path = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            if self.only_variable:
                for star in dataset.variable:
                    pass
            else:
                for star in dataset:
                    pass


@define
class CSVSaveNode(DatasetNode):
    output_location: Path = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass
