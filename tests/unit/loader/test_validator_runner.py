from pathlib import Path
from attr import dataclass
import hypothesis
from shutterbug.file_loader.validator.validator_runner import ValidatorRunner
from shutterbug.file_loader.validator.validators.validator_interface import (
    ValidatorInterface,
)

from hypothesis import given, assume
from hypothesis.strategies import composite, lists, booleans, builds


@dataclass
class ValidatorTest(ValidatorInterface):
    truthiness: bool

    def validate(self, path: Path):
        return self.truthiness


@composite
def list_of_validators(draw) -> ValidatorTest:
    return draw(lists(builds(ValidatorTest, booleans()), min_size=1))


@given(list_of_validators())
def test_validator_runner(validator_list):

    runner = ValidatorRunner(validator_list)
    truth = all(list(map(lambda x: x.validate(""), validator_list)))
    assert runner.validate("") is truth
