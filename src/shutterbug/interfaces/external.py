from abc import abstractmethod, ABC


class CommandInterface(ABC):
    """
    Declares a method for executing a command
    """

    @abstractmethod
    def execute(self):
        raise NotImplementedError
