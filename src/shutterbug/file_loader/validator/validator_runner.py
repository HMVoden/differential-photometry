from pathlib import Path
from typing import List

from attr import dataclass
from shutterbug.file_loader.validator.runner_interface import ValidatorRunnerInterface
from shutterbug.file_loader.validator.validators.validator_interface import (
    ValidatorInterface,
)


@dataclass
class ValidatorRunner(ValidatorRunnerInterface):
    validators: List[ValidatorInterface]

    def validate(self, path: Path):
        for validator in self.validators:
            if validator.validate(path) is False:
                return False
                # TODO put failstate here
        return True
