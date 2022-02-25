import csv
import logging
from pathlib import Path
from typing import Dict, Generator, List, Tuple, Iterable
from more_itertools.recipes import pairwise

from attr import define, field
from more_itertools import consume, map_reduce
from shutterbug.data.star import Star
from shutterbug.data.header import KnownHeader
from shutterbug.data.interfaces.internal import Loader


@define(slots=True)
class CSVLoader(Loader):

    input_file: Path = field()
    headers: KnownHeader = field()
    _stars: Dict[str, List[int]] = field(init=False)

    def _star_count(self) -> Dict[str, List[int]]:
        """Iterates through entire CSV files and finds each star and every index that
        star's name corresponds to, for faster iterating"""
        try:
            return self._stars
        except AttributeError:
            name_index = self.headers.name_index
            rows = self._file_rows()
            # Take enumerated iterable, return header name
            keyfunc = lambda x: x[1][name_index]
            # Take enumerated iterable, return row that this entry belongs on
            valuefunc = lambda x: x[0]
            self._stars = map_reduce(enumerate(rows), keyfunc, valuefunc)
            return self._stars

    def __len__(self):
        """Number of stars in given CSV"""
        return len(self._star_count())

    def _file_rows(self) -> Generator[List[str], None, None]:
        """Skips header and returns an iterable for every row in the input file"""
        filepath = self.input_file
        with open(filepath, newline="", errors="replace", mode="r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip header
            yield from reader

    @staticmethod
    def _row_delta(indices: List[int]) -> Generator[int, None, None]:
        """Calculates the delta between two indices in a list of indexes"""
        if indices[0] == 0:
            # so we don't lose the first row of the first item
            yield 0
        else:
            # So we can consume to just before the item we want
            yield indices[0] - 1
        for first, second in pairwise(indices):
            yield (second - first) - 1

    def _all_rows_in_index(
        self, indices: List[int]
    ) -> Generator[List[str], None, None]:
        """Yields every row for a list of indices"""
        rows = self._file_rows()
        deltas = self._row_delta(indices)
        for delta in deltas:
            consume(rows, delta)
            yield next(rows)

    def _file_stars(self) -> Iterable[Tuple[str, List[List[str]]]]:
        """Yields all data rows in csv from each star in order"""
        stars = self._star_count()
        for name, indices in stars.items():
            rows = list(self._all_rows_in_index(indices))
            yield name, rows

    def __iter__(self) -> Generator[Star, None, None]:
        for star_name, rows in self._file_stars():
            try:
                yield Star.from_rows(rows=rows, row_headers=self.headers)
            except ValueError as e:
                logging.warning(f"Unable to load star {star_name} due to error: {e}")
