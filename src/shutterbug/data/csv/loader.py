import csv
import logging
from operator import itemgetter
from pathlib import Path
from typing import Dict, Generator, List, Union

import numpy as np
from attr import define, field
from more_itertools import bucket, consume, filter_except, ilen, map_reduce
from shutterbug.data.star import Star, StarTimeseries
from shutterbug.data.header import KNOWN_HEADERS, Header, KnownHeader
from shutterbug.data.interfaces.external import FileLoaderInterface


@define
class CSVLoader(FileLoaderInterface):
    READABLE_TYPES = {".xlsx", ".xls", ".xlsm", ".odf", ".ods", ".csv"}

    input_file: Path = field()
    headers: KnownHeader = field(init=False)
    stars: Dict[str, List[int]] = field(init=False)
    count: int = field(init=False)

    @classmethod
    def is_readable(cls, filepath: Path):
        """Verifies if the given file is readable based on suffixes"""
        if filepath.suffix not in cls.READABLE_TYPES:
            return False
        else:
            return True

    def _count_stars(self) -> Dict[str, int]:
        """Iterates through entire CSV files and finds each star and every index that star's name corresponds to, for faster iterating"""
        name_index = self.headers.name_index
        rows = self._file_rows()
        # Take enumerated iterable, return header name
        keyfunc = lambda x: x[1][name_index]
        # Take enumerated iterable, return row that this entry belongs on
        valuefunc = lambda x: x[0]
        result = map_reduce(enumerate(rows), keyfunc, valuefunc)
        return result  # type: ignore

    def __attrs_post_init__(self):
        """Post-initialization attribute creation. Gives count, mode and entire star list to class."""
        self.headers = self._check_headers()

        self.stars = self._count_stars()
        # entry_counts = list(map(len, self.stars.values()))  # type: ignore
        # star_mode, count = mode(entry_counts, axis=None)
        # # Need first entry as these are arrays
        # self.count = count[0]
        # self.star_mode = star_mode[0]

    def __len__(self):
        """Number of stars in given CSV"""
        return len(self.stars)

    def _file_rows(self) -> Generator[List[str], None, None]:
        """Skips header and returns an iterable for every row in the input file"""
        filepath = self.input_file
        with open(filepath, newline="", errors="replace", mode="r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip header
            for row in reader:
                yield row

    def _split_on_name(self):
        "Splits the file into a number of iterables based on header name"
        name_key = self.headers.name_index
        rows = self._file_rows()
        splits = bucket(rows, key=lambda x: x[name_key])
        return splits

    def __iter__(self) -> Generator[Star, None, None]:

        stars = self.stars.items()
        timeseries_getter = self.headers.timeseries_getters
        data_getter = self.headers.star_getters
        star_iterators = self._split_on_name()

        for star, _ in stars:
            iterable = star_iterators[star]
            first_entry = next(iterable)  # get very first entry
            # Only need first entry to create Star type.
            star_type = Star(self.input_file.stem, *data_getter(first_entry))
            data = [timeseries_getter(first_entry)]
            for entry in iterable:
                data.append(timeseries_getter(entry))
            np_data = np.asarray(data)
            star_data = StarTimeseries(np_data[:, 0], np_data[:, 1], np_data[:, 2])
            star_type.data = star_data
            yield star_type

    # everything here and below should be moved out into another function/class
    def _check_headers(self) -> KnownHeader:
        """Verifies loaded file header against known headers and returns known header"""
        raw_headers = self._read_file_header()
        headers = Header(headers=self._clean_headers(raw_headers))

        for known in KNOWN_HEADERS:
            if headers == known:
                logging.debug(f"Input file matches header type {known.name}")
                return known
        raise ValueError("Cannot load file, unknown headers")

    def _read_file_header(self) -> List[str]:
        """Reads the first line in a csv file and returns the raw headers"""
        with open(self.input_file, newline="") as f:
            try:
                reader = csv.reader(f)
                raw_headers = next(reader)
            except StopIteration:
                raise ValueError(
                    f"File {self.input_file.name} does not contain headers, cannot continue"
                )
        return raw_headers

    def _clean_headers(self, headers: List[str]) -> List[str]:
        """Removes all unnecessary whitespace, newlines and tabs from every string in a list"""
        cleaned = []
        for header in headers:
            cleaned.append(header.strip())
        return cleaned
