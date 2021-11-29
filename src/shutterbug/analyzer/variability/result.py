from dataclasses import dataclass
from typing import Literal


@dataclass
class TestResult:
    null: Literal["accept", "reject"]
    pvalue: float
