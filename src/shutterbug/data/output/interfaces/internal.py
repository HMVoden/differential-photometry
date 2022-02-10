from abc import ABC, abstractmethod


class GraphInterface(ABC):
    @abstractmethod
    def render(self):
        raise NotImplementedError
