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
            output_folder = self.output_location / dataset.name
            variable_folder = output_folder / "variable"
            nonvariable_folder = output_folder / "nonvariable"
            output_folder.mkdir(exist_ok=True, parents=True)
            variable_folder.mkdir(exist_ok=True)
            nonvariable_folder.mkdir(exist_ok=True)
            builder = self.graph_builder
            logging.debug(f"Outputting graphs to folder {output_folder}")
            if self.only_variable:
                stars = dataset.variable
            else:
                stars = dataset
            for star in stars:
                title = f"Differential magnitude of {star.name} \n X: {star.x} Y: {star.y} \n"
                for feature, value in star.timeseries.features.items():
                    title += "{feature}: {value}"
                builder.title = title
                builder.axis_names = ("Time (UTC)", "Differential Magnitude")
                builder.axis_limits = (1, 1)
                builder.data = star.timeseries.differential_magnitude
                builder.error = star.timeseries.differential_error
                graph = builder.build()
                logging.debug(f"Writing graph {star.name}")
                if star.variable:
                    graph.save(variable_folder / f"{star.name}.png")
                else:
                    graph.save(nonvariable_folder / f"{star.name}.png")
                builder.reset()
            yield dataset


@define
class CSVSaveNode(DatasetNode):
    output_location: Path = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass
