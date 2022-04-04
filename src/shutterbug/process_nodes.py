import logging
from typing import Generator, List

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
        for dataset in self.datasets.execute():
            logging.debug(
                f"Executing Variability node on current dataset, {dataset.name}"
            )
            for star in dataset:
                logging.debug(f"Testing star {star.name}")
                for feature in self.features:
                    star = run_test(star=star, test=feature)
                star = is_variable(star, threshold=self.threshhold)
                dataset.update(star)
            yield dataset


@define
class DifferentialNode(DatasetNode):
    photometer: Photometer = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            logging.debug(
                f"Executing Differential node on current dataset, {dataset.name}"
            )
            for star in dataset:
                logging.debug(f"Calculating differential magnitudes on {star.name}")
                star = self.photometer.average_differential(
                    target=star, reference=dataset.similar_to(star)
                )
                dataset.update(star)
            yield dataset
