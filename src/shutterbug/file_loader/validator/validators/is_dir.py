from pathlib import Path
from shutterbug.file_loader.validator.validators.validator_interface import (
    ValidatorInterface,
)


class IsDirectoryValidator(ValidatorInterface):
    def validate(self, path: Path) -> bool:
        return path.is_dir()
