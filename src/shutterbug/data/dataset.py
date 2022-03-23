from functools import singledispatch
from typing import Generator, List

from attr import define, field
from shutterbug.data.interfaces.internal import Reader, Writer
from shutterbug.data.star import Star


@define
class Dataset:
    name: str = field()
    reader: Reader = field()
    writer: Writer = field()

    def __iter__(self) -> Generator[Star, None, None]:
        yield from self.reader

    def __len__(self) -> int:
        return len(self.reader.names)

    @singledispatch
    def update(self, star: Star):
        self.writer.write(star, overwrite=True)

    @update.register
    def _(self, star: list):
        self.writer.write(star, overwrite=True)

    def similar_to(self, star: Star) -> List[Star]:
        return self.reader.similar_to(star)
