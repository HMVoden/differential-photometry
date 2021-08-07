import logging
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import shutterbug.config.manager as config
import xarray as xr
from natsort import natsort_keygen


def extract(filename: Path) -> pd.DataFrame:
    """Assuming there are headers in the data file, this takes the filename opens it and reads it
    into a pandas dataframe, cleans the headers to make it all lowercase with no parenthesis and returns only
    the columns we're interested in.

    Parameters
    ----------
    filename : str
        Filename of datafile

    Returns
    -------
    pd.DataFrame
        Dataframe containing required columns, trimmed and made usable
    """

    input_config = config.get("input")
    filetype = input_config["types"][filename.suffix]
    file_config = input_config[filetype]
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


def get_file_list(file_list: Tuple[Path, ...]) -> List[Path]:
    result = []
    readable_types = config.get("input")["types"]
    for path in file_list:
        if path.is_dir():
            files = [x for x in path.iterdir() if x.suffix in readable_types.keys()]
            result.extend(files)
        else:
            if path.suffix in readable_types.keys():
                result.append(path)
    return result
