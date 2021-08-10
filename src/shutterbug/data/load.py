import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import xarray as xr


def from_file(filename: Path, reader_config: Dict) -> xr.Dataset:
    filetype = reader_config["types"][filename.suffix]
    file_config = reader_config[filetype]
    if file_config["module"] == "pd":
        ds = open_pandas(
            filename=filename,
            reader=file_config["reader"],
            settings=file_config["settings"],
        )
    elif file_config["module"] == "xr":
        ds = open_xr(
            filename=filename,
            reader=file_config["reader"],
            settings=file_config["settings"],
        )
    else:
        raise NotImplementedError

    return ds


# TODO make these one function
def open_pandas(filename: Path, reader: str, settings: Dict):
    reader_func = getattr(pd, reader)
    df = reader_func(filename, **settings)
    df = df.to_xarray()
    return df


def open_xr(filename: Path, reader: str, settings: Dict):
    reader_func = getattr(xr, reader)
    ds = reader_func(filename, **settings)
    return ds
