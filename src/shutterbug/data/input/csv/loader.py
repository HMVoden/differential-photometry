import csv
import logging
from functools import partial
from pathlib import Path
from typing import Dict, List

import numpy as np
from attr import define, field
from more_itertools import consume, filter_except, ilen, map_reduce
from scipy.stats import mode
from shutterbug.data.core.star import Star
from shutterbug.data.input.csv.header import KnownHeader


@define
class CSVLoader:
    READABLE_TYPES = {".xlsx", ".xls", ".xlsm", ".odf", ".ods", ".csv"}

    input_file: Path
    headers: KnownHeader
    stars: Dict[str, List[int]] = field(init=False)
    star_mode: int = field(init=False)
    count: int = field(init=False)

    def _count_unique_stars(self) -> Dict[str, int]:
        filepath = self.input_file
        headers = self.headers.headers
        star_key = self.headers.star_name
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f, fieldnames=headers)
            next(reader)  # skip header
            keyfunc = lambda x: x[1][star_key]
            valuefunc = lambda x: x[0]
            result = map_reduce(enumerate(reader), keyfunc, valuefunc)
        return result

    def __attrs_post_init__(self):
        self.stars = self._count_unique_stars()
        entry_counts = list(map(len, self.stars.values()))
        star_mode, count = mode(entry_counts, axis=None)
        # Need first entry as these are arrays
        self.count = count[0]
        self.star_mode = star_mode[0]

    def __len__(self):
        return self.count

    @staticmethod
    def _compare_strings(other: Dict[str, str], name: str, name_key: str) -> str:
        other_name = other[name_key]
        if name == other_name:
            return name
        raise ValueError(f"Expected name {name}, received name {other_name}")

    def __iter__(self):
        stars = self.stars.items()
        star_mode = self.star_mode
        filepath = self.input_file
        headers = self.headers.headers
        name_key = self.headers.star_name
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f, fieldnames=headers)
            for star, entries in stars:
                if len(entries) != star_mode:
                    logging.warning(
                        f"Star {star} has {len(entries)} data entries, expected {star_mode}. Skipping star."
                    )
                    continue

                next(reader)  # skip header

                mag = []
                error = []
                time = []
                consume(reader, entries[0])
                first_entry = next(reader)  # get very first entry
                mag.append(first_entry["Mag"])
                error.append(first_entry["Error"])
                time.append(first_entry["JD"])
                for idx, entry in enumerate(entries):
                    if not (idx + 1 >= len(entries)):
                        next_entry = entries[idx + 1]
                        delta = next_entry - entry
                        consume(reader, delta)
                        data = next(reader)
                        mag.append(data["Mag"])
                        error.append(data["Error"])
                        time.append(data["JD"])

                x = first_entry["X"]
                y = first_entry["Y"]
                dataset_name = first_entry["Name"]
                yield Star(
                    dataset=self.input_file.name,
                    name=dataset_name,
                    x=x,
                    y=y,
                    jd=time,
                    mag=mag,
                    error=error,
                )
                f.seek(0)
