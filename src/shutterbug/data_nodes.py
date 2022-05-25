from __future__ import annotations

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Generator, Union

from attr import define, field

from shutterbug.application import make_output_folder
from shutterbug.data import BuilderBase, Dataset
from shutterbug.data.interfaces.external import Loader
from shutterbug.data.interfaces.internal import Writer
from shutterbug.interfaces.external import ControlNode


@define
class DatasetNode(ControlNode):
    datasets: Union[DatasetNode, DatasetLeaf] = field()

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
        logging.info("Storing dataset")
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
            folder = make_output_folder(
                dataset_name=dataset.name, output_folder=self.output_location
            )
            builder = self.graph_builder
            logging.info(f"Outputting graphs to folder {folder}")
            if self.only_variable:
                stars = dataset.variable
            else:
                stars = dataset.__iter__()
            for star in stars:
                title = f"Differential magnitude of {star.name} \n x: {star.x} y: {star.y} \n"
                builder.title = title
                builder.axis_names = ("Time (UTC)", "Differential Magnitude")
                builder.axis_limits = (1.25, 1.25)
                builder.size = (5, 5)
                builder.data = star.timeseries.differential_magnitude
                builder.error = star.timeseries.differential_error
                builder.features = star.timeseries.features
                graph = builder.build()
                logging.debug(f"Writing graph {star.name}")
                if star.variable:
                    graph.save(folder / "variable" / f"{star.name}.png")
                else:
                    graph.save(folder / "nonvariable" / f"{star.name}.png")
                builder.reset()
            yield dataset


@define
class CSVSaveNode(DatasetNode):
    output_location: Path = field()
    only_variable: bool = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            folder = make_output_folder(
                dataset_name=dataset.name, output_folder=self.output_location
            )
            filename = folder / dataset.name / "_result.csv"
            if (filename).exists():
                # clobber file
                with open(filename, "w") as f:
                    pass
            if self.only_variable:
                stars = dataset.variable
            else:
                stars = dataset.__iter__()
            for star in stars:
                df = star.to_dataframe()
                df.to_csv(filename, mode="a")
            yield dataset
