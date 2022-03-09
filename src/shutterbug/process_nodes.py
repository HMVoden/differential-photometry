import logging
from typing import Dict, Generator, List

from attr import define, field

from shutterbug.analysis.feature import FeatureBase
from shutterbug.analysis.variable import is_variable, run_test
from shutterbug.data import Dataset
from shutterbug.data_nodes import DatasetNode
from shutterbug.interfaces.internal import Photometer


@define
class VariabilityNode(DatasetNode):
    features: List[FeatureBase] = field()
    threshhold: float

    def execute(self) -> Generator[Dataset, None, None]:
        logging.debug("Executing Variability node")
        for dataset in self.datasets.execute():
            for star in dataset:
                for feature in self.features:
                    star = run_test(data=star, test=feature)
                star = is_variable(star, threshold=self.threshhold)
                dataset.update(star)
            yield dataset


@define
class DifferentialNode(DatasetNode):
    photometer: Photometer = field()

    def execute(self) -> Generator[Dataset, None, None]:
        logging.debug("Executing Differential node")
        for dataset in self.datasets.execute():
            for star in dataset:
                star = self.photometer.average_differential(
                    target=star, reference=dataset.similar_to(star)
                )
                dataset.update(star)
            yield dataset
