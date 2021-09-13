from pathlib import Path
from abc import abstractmethod, ABC
from typing import Dict


class FrameLoaderInterface(ABC):
    @abstractmethod
    def load(path: Path, **settings: Dict):
        pass
