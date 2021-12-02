from typing import Iterable

import attr


@attr.s
class Star:
    name: str = attr.ib(init=False)
    dataset: str = attr.ib()
    dataset_name: str = attr.ib()
    x: int = attr.ib()
    y: int = attr.ib()
    ra: float = attr.ib(init=False)
    dec: float = attr.ib(init=False)
    jd: float = attr.ib()
    mag: float = attr.ib()
    error: float = attr.ib()

    @error.validator
    def positive_error(self, attribute, value):
        if not value >= 0:
            raise ValueError("Cannot have negative error")
