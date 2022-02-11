from attrs import field, define
from typing import Tuple, Optional, Iterable


@define
class Graph:
    """Generic Graph"""

    _title: Optional[str] = field(init=False, default=None)
    _axis_names: Tuple[Optional[str], Optional[str]] = field(
        init=False, default=(None, None)
    )
    _size: Tuple[Optional[int], Optional[int]] = field(init=False, default=(None, None))
    _x: Iterable[float] = field(init=False)
    _y: Iterable[float] = field(init=False)
    _type: Optional[str] = field(init=False, default=None)

    @property
    def title(self):
        raise NotImplementedError

    @property
    def axis_names(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def x(self):
        raise NotImplementedError

    @property
    def y(self):
        raise NotImplementedError

    @property
    def type(self):
        raise NotImplementedError
