from functools import singledispatch
from typing import Generator
from attr import field, define

from shutterbug.data.interfaces.internal import Loader, Writer
from shutterbug.data.star import Star


@define
class Dataset:
    name: str = field()
    reader: Loader = field()
    writer: Writer = field()

    def __iter__(self) -> Generator[Star, None, None]:
        yield from self.reader

    @singledispatch
    def update(self, star: Star):
        self.writer.write(star, overwrite=True)

    @update.register
    def _(self, star: list):
        self.writer.write(star, overwrite=True)
