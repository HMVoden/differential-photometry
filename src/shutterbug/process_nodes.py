from shutterbug.data_nodes import DatasetNode
from typing import Generator
from shutterbug.data import Dataset
from attr import define, field

from shutterbug.interfaces.internal import Photometer


@define
class FeaturesNode(DatasetNode):
    datasets: DatasetNode = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass


@define
class VariabilityNode(DatasetNode):
    datasets: DatasetNode = field()

    def execute(self) -> Generator[Dataset, None, None]:
        pass


@define
class DifferentialNode(DatasetNode):
    datasets: DatasetNode = field()
    photometer: Photometer = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            for star in dataset:
                star = self.photometer.average_differential(
                    target=star, reference=dataset.similar_to(star)
                )
                dataset.update(star)
            yield dataset
