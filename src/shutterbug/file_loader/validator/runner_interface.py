from pathlib import Path
from abc import abstractmethod, ABC


class ValidatorRunnerInterface(ABC):
    # @property
    # @classmethod
    # @abstractmethod
    # def validators(cls):
    #     raise NotImplementedError

    @abstractmethod
    def validate(self, path: Path):
        pass
