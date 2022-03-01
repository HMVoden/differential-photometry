from shutterbug.analysis.feature import FeatureBase
from shutterbug.analysis.variable import is_variable, run_test
from shutterbug.data_nodes import DatasetNode
from typing import Dict, Generator, List
from shutterbug.data import Dataset
from attr import define, field

from shutterbug.interfaces.internal import Photometer


@define
class VariabilityNode(DatasetNode):
    datasets: DatasetNode = field()
    features: List[FeatureBase] = field()
    threshholds: Dict[str, float]

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            for star in dataset:
                for feature in self.features:
                    star = run_test(data=star, test=feature)
                star = is_variable(star, thresholds=self.threshholds)
                dataset.update(star)
            yield dataset


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
