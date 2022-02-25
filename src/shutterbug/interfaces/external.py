from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Any, Optional


class ControlNode(ABC):
    @abstractmethod
    def execute(self) -> Any:
        raise NotImplementedError
