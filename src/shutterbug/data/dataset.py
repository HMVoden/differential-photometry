import logging
from functools import singledispatch
from itertools import repeat
from typing import Dict, Generator, List, Union

from attr import define, field
from shutterbug.data.interfaces.internal import Reader, Writer
from shutterbug.data.star import Star


@define
class Dataset:
    name: str = field()
    reader: Reader = field()
    writer: Writer = field()
    store_in_memory: bool = field()
    _star_cache: Dict[str, Union[Star, None]] = field(init=False, default={})

    def __attrs_post_init__(self):
        if self.store_in_memory is True:
            self._star_cache = dict(zip(self.reader.names, repeat(None)))

    def __iter__(self) -> Generator[Star, None, None]:
        cache = self._star_cache
        if self.store_in_memory is True:
            for name, star in cache.items():
                if star is None:
                    star = self.reader.get(name)
                    logging.debug(f"Caching star {star.name}")
                    cache[name] = self.reader.get(name)
                yield star
        else:
            yield from self.reader

    def __len__(self) -> int:
        return len(self.reader.names)

    @singledispatch
    def update(self, star: Star):
        logging.debug(f"Updating star {star.name} in reader")
        self.writer.update(star)

    @update.register
    def _(self, star: list):
        logging.debug(f"Updating stars {[x.name for x in star]} in reader")
        self.writer.update(star)

    def similar_to(self, star: Star) -> List[Star]:
        if self.store_in_memory is True:
            to_get = []
            stars = []
            for name in self.reader.similar_to(star):
                if self._star_cache[name] is None:
                    to_get.append(name)
                else:
                    stars.append(self._star_cache[name])
            logging.debug(f"Stars {to_get} are not in cache, fetching from reader")
            from_reader = self.reader.get_many(to_get)
            for star in from_reader:
                self._star_cache[star.name] = star
            stars.extend(from_reader)
            return stars
        else:
            names = self.reader.similar_to(star)
            logging.debug(
                f"Stars {names} being fetched for use in processing {star.name}"
            )
            return self.reader.get_many(names)

    @property
    def variable(self) -> Generator[Star, None, None]:
        logging.info(
            f"Fetching all known variable stars from reader in dataset {self.name}"
        )
        yield from self.reader.variable
