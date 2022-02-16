from abc import abstractmethod
from attrs import field, define

from shutterbug.data.interfaces.external import GraphBuilderInterface
from typing import Literal, Optional, Tuple
import pandas as pd

from shutterbug.data.interfaces.internal import GraphInterface
from shutterbug.data.star import Star, StarTimeseries


@define
class BuilderBase(GraphBuilderInterface):
    """Generic builder type, contains all fields and properties for building"""

    _title: Optional[str] = field(init=False)
    _axis_names: Tuple[Optional[str], Optional[str]] = field(init=False)
    _axis_limits: Tuple[Optional[float], Optional[float]] = field(init=False)
    _data: pd.DataFrame = field(init=False)
    _size: Tuple[Optional[int], Optional[int]] = field(init=False)

    _type: Literal["scatter", "line"] = field(init=False, default="scatter")
    _error_display: Literal["bar", "fill", None] = field(init=False, default="bar")

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def axis_names(self) -> Tuple[Optional[str], Optional[str]]:
        return self._axis_names

    @property
    def axis_limits(self) -> Tuple[Optional[float], Optional[float]]:
        return self._axis_limits

    @property
    def size(self) -> Tuple[Optional[float], Optional[float]]:
        return self._size

    @property
    def type(self) -> Optional[str]:
        return self._type

    @property
    def data(self) -> pd.DataFrame:
        # Don't return mutable data, only copies
        return self._data.copy(deep=True)

    @property
    def error_display(self) -> Literal["bar", "fill", None]:
        return self._error_display

    def reset(self) -> None:
        self._title = None
        self._axis_names = (None, None)
        # set dtype to avoid deprecation warning
        # float16 to keep it small
        self._data = pd.DataFrame(dtype="float16")
        self._size = (None, None)
        self._type = "scatter"
        self._error_display = "bar"

    @abstractmethod
    def build(self) -> GraphInterface:
        raise NotImplementedError
