from typing import Iterable, List

from attr import define, field


@define
class Star:
    dataset: str = field()
    name: str = field()
    x: int = field()
    y: int = field()
    jd: List[float] = field()
    mag: List[float] = field()
    error: List[float] = field()

    # @error.validator
    # def positive_error(self, attribute, value):
    #     if not value >= 0:
    #         raise ValueError("Cannot have negative error")
