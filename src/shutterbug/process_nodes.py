import logging
from typing import Generator, List

from attr import define, field

from shutterbug.analysis.feature import FeatureBase
from shutterbug.analysis.variable import run_test, test_variability
from shutterbug.data import Dataset
from shutterbug.data_nodes import DatasetNode
from shutterbug.interfaces.internal import Photometer


@define
class VariabilityNode(DatasetNode):
    tests: List[FeatureBase] = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            logging.info(f"Executing Variability test on current dataset")
            logging.info(f"Using tests: {[x.name for x in self.tests]}")
            for star in dataset:
                logging.info(f"Testing star {star.name}")
                for test in self.tests:
                    star = run_test(star=star, test=test)
                star = test_variability(star, self.tests)
                dataset.update(star)
            yield dataset


@define
class DifferentialNode(DatasetNode):
    photometer: Photometer = field()

    def execute(self) -> Generator[Dataset, None, None]:
        for dataset in self.datasets.execute():
            logging.info(f"Executing Differential calculation on current dataset")
            for star in dataset:
                logging.info(f"Calculating differential magnitudes on {star.name}")
                star = self.photometer.average_differential(
                    target=star, reference=dataset.similar_to(star)
                )
                dataset.update(star)
            dataset.flush_write()
            yield dataset
