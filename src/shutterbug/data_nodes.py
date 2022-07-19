from __future__ import annotations

import logging
from abc import abstractmethod
from pathlib import Path
from typing import Generator, List, Union, Optional

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
    names: List[str]= field()

    def execute(self) -> None:
        logging.info("Storing dataset")
        names = self.names
        source = self.source
        stars = []
        if len(names) == len(source.names):
            for star in self.source:
                if star is not None:
                    stars.append(star)
                if len(stars) >= 50:
                    self.writer.write(stars)
                    stars = []
        else:
            for name in names:
                star = source.get(name)
                if star is not None:
                    stars.append(star)
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
                logging.info(f"Creating graph for star: {star.name}")
                try:
                    title = f"Differential magnitude of {star.name} \n x: {star.x} y: {star.y} \n"
                    builder.title = title
                    builder.axis_names = ("Time (UTC)", "Differential Magnitude")
                    builder.axis_limits = (1.25, 1.25)
                    builder.size = (5, 5)
                    builder.data = star.timeseries.differential_magnitude
                    builder.error = star.timeseries.differential_error
                    builder.features = star.timeseries.features
                    graph = builder.build()
                    logging.info(f"Writing graph {star.name}")
                    if star.variable:
                        graph.save(folder / "variable" / f"{star.name}.png")
                    else:
                        graph.save(folder / "nonvariable" / f"{star.name}.png")
                except ValueError as e:
                    logging.error(f"Unable to create graph for star {star.name}, received error: {e}")
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
            filename = folder / f"{dataset.name}_result.csv"
            logging.info(f"Outputting data to file {filename}")
            # clobber and create file
            with open(filename, "w") as _:
                pass
            if self.only_variable:
                stars = dataset.variable
            else:
                stars = dataset.__iter__()
            # First instance writes the header, no more than this needed
            next(stars).to_dataframe().to_csv(filename, mode="a", header=True)
            for star in stars:
                logging.debug(f"Writing star {star.name} to file")
                df = star.to_dataframe()
                df.to_csv(filename, mode="a", header=False)
            yield dataset
