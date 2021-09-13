from pathlib import Path
from shutterbug.file_loader.validator.validators.validator_interface import (
    ValidatorInterface,
)


class ExistsValidator(ValidatorInterface):
    def validate(self, path: Path) -> bool:
        return path.exists()
