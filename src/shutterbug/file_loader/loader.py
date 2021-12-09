from pathlib import Path
from typing import Generator, Iterator, List, Tuple

import pandas as pd

# Kept as module not class-in-a-module
# as, while this has sufficient ability to be
# made into a class, it is used exactly once
# then never again


_suffix_to_loader = {
    ".xlsx": pd.read_excel,
    ".xls": pd.read_excel,
    ".xlsm": pd.read_excel,
    ".odf": pd.read_excel,
    ".ods": pd.read_excel,
    ".csv": pd.read_csv,
    ".parquet": pd.read_parquet,
    # ".hd5": xr.open_dataset,
    # ".nc": xr.open_dataset,
}  # still don't like this, but can't think of better method
# strategy pattern?
# TODO investigate strategy pattern and see if viable to implement here
# TODO investigate factory pattern to see if useable with strategy in this case


def _is_accepted_format(path: Path) -> bool:
    if path.suffix in _suffix_to_loader.keys():
        return True
    return False


def _filter_unreadable_paths(paths: List[Path]) -> Iterator:
    return filter(_is_accepted_format, paths)


def _get_files_from_paths(paths: List[Path]):
    result = []
    for path in paths:
        if path.is_dir():
            files = [x for x in path.iterdir() if x.is_file()]
            result.extend(files)
        elif path.is_file():
            result.append(path)
    return result


def _load_from_suffix(path: Path, **settings) -> pd.DataFrame:
    suffix = path.suffix
    return _suffix_to_loader[suffix](path, **settings)


def iload(
    paths: List[Path], **settings
) -> Generator[Tuple[str, pd.DataFrame], None, None]:
    paths = _get_files_from_paths(paths)
    paths = list(_filter_unreadable_paths(paths))
    if len(paths) == 0:
        raise ValueError(
            f"No readable files given, readable formats are: {' '.join(_suffix_to_loader.keys())}"
        )
    for path in paths:
        yield path.stem, _load_from_suffix(path, **settings)


def load(path: Path, **settings) -> Tuple[str, pd.DataFrame]:
    if _is_accepted_format(path):
        return path.stem, _load_from_suffix(path, **settings)
    else:
        raise ValueError(
            f"Not a readable type, given filetype {path.suffix}, readable formats are {' '.join(_suffix_to_loader.keys())}"
        )


def get_readable_file_count(paths: List[Path]) -> int:
    paths = _get_files_from_paths(paths)
    return len(list(_filter_unreadable_paths(paths)))
