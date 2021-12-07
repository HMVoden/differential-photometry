import csv
import logging
from functools import partial
from operator import itemgetter
from pathlib import Path
from typing import Dict, Generator, List

import numpy as np
from attr import define, field
from more_itertools import bucket, consume, filter_except, ilen, map_reduce
from scipy.stats import mode
from shutterbug.data.core.star import Star, StarTimeseries
from shutterbug.data.input.csv.header import KnownHeader


@define
class CSVLoader:
    READABLE_TYPES = {".xlsx", ".xls", ".xlsm", ".odf", ".ods", ".csv"}

    input_file: Path
    headers: KnownHeader
    stars: Dict[str, List[int]] = field(init=False)
    star_mode: int = field(init=False)
    count: int = field(init=False)

    def _count_stars(self) -> Dict[str, int]:
        """Iterates through entire CSV files and finds each star and every index that star's name corresponds to, for faster iterating (Not yet implemented)"""
        name_index = self.headers.get_name_index()
        rows = self._file_rows()
        keyfunc = lambda x: x[1][name_index]
        valuefunc = lambda x: x[0]
        result = map_reduce(enumerate(rows), keyfunc, valuefunc)
        return result  # type: ignore

    def __attrs_post_init__(self):
        """Post-initialization attribute creation. Gives count, mode and entire star list to class."""
        self.stars = self._count_stars()
        entry_counts = list(map(len, self.stars.values()))  # type: ignore
        star_mode, count = mode(entry_counts, axis=None)
        # Need first entry as these are arrays
        self.count = count[0]
        self.star_mode = star_mode[0]

    def __len__(self):
        """Number of stars in given CSV"""
        return self.count

    def _file_rows(self) -> Generator[List[str], None, None]:
        """Skips header and returns an iterable for every row in the input file"""
        filepath = self.input_file
        with open(filepath, newline="", errors="replace", mode="r") as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # skip header
            for row in reader:
                yield row

    def __iter__(self) -> Generator[Star, None, None]:
        stars = self.stars.items()
        star_mode = self.star_mode
        name_key = self.headers.get_name_index()
        timeseries_indices = self.headers.get_timeseries_indices()
        timeseries_getter = itemgetter(*timeseries_indices)
        data_indices = self.headers.get_star_indices()
        data_getter = itemgetter(*data_indices)
        rows = self._file_rows()
        star_iterators = bucket(rows, key=lambda x: x[name_key])
        for star, entries in stars:
            if len(entries) != star_mode:
                logging.warning(
                    f"Star {star} has {len(entries)} data entries, expected {star_mode}. Skipping star."
                )
                continue
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
