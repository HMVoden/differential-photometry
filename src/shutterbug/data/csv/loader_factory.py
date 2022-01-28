from pathlib import Path
import logging
from shutterbug.data.csv.loader import CSVLoader
from shutterbug.data.header import Header, KnownHeader, KNOWN_HEADERS
from typing import List
import csv

READABLE_TYPES = {".xlsx", ".xls", ".xlsm", ".odf", ".ods", ".csv"}


def make_loader(file_path: Path) -> CSVLoader:
    headers = _headers_from_file(file_path)
    return CSVLoader(input_file=file_path, headers=headers)


def _headers_from_file(file_path: Path) -> KnownHeader:
    """Verifies loaded file header against known headers and returns known header"""
    raw_headers = _read_file_header(file_path)
    headers = Header(raw_headers)

    for known in KNOWN_HEADERS:
        if headers == known:
            known.headers = headers.headers
            logging.debug(f"Input file matches header type {known.header_origin}")
            return known
    raise ValueError("Cannot load file, unknown headers")


def _read_file_header(file_path: Path) -> List[str]:
    """Reads the first line in a csv file and returns the raw headers"""
    with open(file_path, newline="") as f:
        try:
            reader = csv.reader(f)
            raw_headers = next(reader)
        except StopIteration:
            raise ValueError(
                f"File {file_path.name} does not contain headers, cannot continue"
            )
    return raw_headers
