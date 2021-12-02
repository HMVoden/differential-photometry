import csv
import logging
from pathlib import Path
from typing import Dict, List, Mapping

import numpy as np
from attr import define, field
from more_itertools import ilen, map_reduce
from scipy.stats import mode
from shutterbug.data.input.csv.header import KnownHeader


@define
class CSVLoader:
    READABLE_TYPES = {".xlsx", ".xls", ".xlsm", ".odf", ".ods", ".csv"}

    input_file: Path
    headers: KnownHeader
    rows: int = field(init=False)
    stars: Dict[str, int] = field(init=False)
    star_mode: int = field(init=False)
    count: int = field(init=False)

    def _count_rows(self) -> int:
        filepath = self.input_file
        with open(filepath, newline="") as f:
            num_rows = ilen(f) - 1  # remove one for header row
        return num_rows

    def _count_unique_stars(self) -> Mapping[str, int]:
        filepath = self.input_file
        headers = self.headers.headers
        star_key = self.headers.star_name
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f, fieldnames=headers)
            next(reader)  # skip header
            keyfunc = lambda x: x[star_key]
            valuefunc = lambda x: 1
            reducefunc = sum
            result = map_reduce(reader, keyfunc, valuefunc, reducefunc)
        return result

    def __attrs_post_init__(self):
        self.rows = self._count_rows()
        self.stars = self._count_unique_stars()
        star_mode, count = mode(list(self.stars.values()), axis=None)
        # Need first entry as these are arrays
        self.count = count[0]
        self.star_mode = star_mode[0]

    def __len__(self):
        return self.count

    def __iter__(self):
        stars = self.stars
        star_mode = self.star_mode
        for star, entries in stars:
            if entries != star_mode:
                logging.warning(
                    f"Star {star} has {entries} data entries, expected {star_mode}. Skipping star."
                )
                continue
