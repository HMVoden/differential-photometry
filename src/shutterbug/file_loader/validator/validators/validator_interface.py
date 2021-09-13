from pathlib import Path
import attr
from abc import abstractmethod, ABC


class ValidatorInterface(ABC):
    @abstractmethod
    def validate(self, path: Path):
        pass
