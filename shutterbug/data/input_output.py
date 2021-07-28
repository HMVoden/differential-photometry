import logging
from pathlib import Path
from typing import Dict, List, Tuple

import config.manager as config
import pandas as pd
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


def save_to_csv(
    ds: xr.Dataset,
    filename: str,
    output_flag: bool,
    offset: bool = None,
    output_folder: Path = None,
):
    """Saves specified dataframe to csv, changes filename based on inputted filename,
    how the dataframe is to be sorted and split.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe to write
    filename : str
        base output filename
    sort_on : List[str], optional
        List of column names to sort dataframe on, using natural sorting, by default None
    split_on : List[str], optional
        List of column names to split the dataframe on, by default None
    output_folder: Path, optional
        Root directory to output files to, by default None
    """
    if output_flag == True:
        logging.info("Outputting processed dataset as csv...")

        df = ds.to_dataframe().reset_index()
        df = df.sort_values(["star", "time"], key=natsort_keygen())
        output_config = config.get("output")

        output_dict = {}
        if output_folder is None:
            output_folder = Path.cwd()
            output_dict.update(**output_config["base"])
            output_dict.update(**output_config["csv"])
        else:
            output_folder = Path(output_folder)

        if offset == True:
            output_dict.update(**output_config["corrected"])
        # end ifs
        output_folder = output_folder.joinpath(*output_dict.values())
        if not output_folder.exists():
            logging.info("Creating directory %s", output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

        out_name = "processed_{0}.csv".format(filename)
        out_file = output_folder.joinpath(out_name)
        logging.info("Writing out %s", out_file)
        df.to_csv(out_file)
        logging.info("Finished excel output")
    return ds


def generate_graph_output_path(
    offset: bool = False,
    inter_varying: bool = False,
    intra_varying: bool = False,
    uniform: bool = False,
    root: Path = None,
) -> Path:
    """Generates the output path based on configured features.

    Parameters
    ----------
    offset : bool, optional
        Whether or not the dataframe has been offset corrected, by default False.
    varying : bool, optional
        Whether or not the dataframe data is varying, by default False.
    brief : bool, optional
        Whether or not the data is briefly varying, by default False.
    split : bool, optional
        Whether or not the dataframe is split, by default False.
    uniform : bool, optional
        Whether or not the graphing has a uniform y-axis, by default False.
    root: Path, optional
        Root directory to output files to, by default None

    Returns
    -------
    Path
        A path object of the folder to write to.
    """
    output_config = config.get("output")

    output_dict = {}
    if root is None:
        output_path = Path.cwd()  # current directory of script
    else:
        output_path = root
    output_dict.update(**output_config["base"])
    dataset = config.get("filename")
    output_dict["dataset"] = dataset.stem.split("_")[0]
    output_dict["input_filename"] = dataset.stem
    if uniform == True:
        output_dict.update(**output_config["uniform"])
    if offset == True:
        output_dict.update(**output_config["corrected"])
    if inter_varying == True and intra_varying == True:
        output_dict.update(**output_config["always_varying"])
    elif inter_varying == True and intra_varying == False:
        output_dict.update(**output_config["inter_varying"])
    elif inter_varying == False and intra_varying == True:
        output_dict.update(**output_config["briefly_varying"])
    else:
        output_dict.update(**output_config["non_varying"])

    output_path = output_path.joinpath(*output_dict.values())
    return output_path


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
