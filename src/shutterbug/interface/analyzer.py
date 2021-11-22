from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd
from shutterbug.analyzer.interface.constraints import ConstraintInterface
from shutterbug.analyzer.interface.differential import \
    DifferentialCalculatorInterface
from shutterbug.analyzer.interface.variability import \
    VariabilityDetectionInterface


@dataclass
class AnalyzerCoreInterface(ABC):
    constraint: ConstraintInterface
    differential_calculator: DifferentialCalculatorInterface
    variability_tester: VariabilityDetectionInterface

    @abstractmethod
    def analyze(self, data: pd.DataFrame):
        raise NotImplementedError
