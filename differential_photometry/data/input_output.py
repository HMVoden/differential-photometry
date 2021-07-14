import logging
from os import PathLike
from pathlib import Path, PurePath
from typing import List, Tuple

import numpy as np
import pandas as pd
import differential_photometry.data.sanitize as sanitize
from natsort import natsort_keygen

import config.manager as config


def extract(filename: str) -> pd.DataFrame:
    """ Assuming there are headers in the data file, this takes the filename opens it and reads it
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
    data_path = PurePath(filename)
    if (data_path.suffix == ".xlsx"
        ):  # This way we can ignore if it's a csv or excel file
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    required_column_names = np.array(
        ["obj", "name", "mag", "error", "x", "y", "jd"])
    df = sanitize.clean_headers(df, required_column_names)
    df = sanitize.clean_data(df)
    # This might be better as its own function
    if "jd" in df.columns:
        df["time"] = pd.to_datetime(df["jd"], origin="julian", unit="D")
        unique_years = df["time"].dt.year.unique()
        unique_months = df["time"].dt.month.unique()
        unique_days = df["time"].dt.day.unique()
        df["d_m_y"] = df["time"].dt.strftime("%d-%m-%Y")

        logging.info("Number of days found in dataset: %s", len(unique_days))
        logging.info("Number of months found in dataset: %s",
                     len(unique_months))
        logging.info("Number of years found in dataset: %s", len(unique_years))
    return df


def save_to_excel(df: pd.DataFrame,
                  filename: str,
                  sort_on: List[str] = None,
                  split_on: List[str] = None,
                  corrected: bool = None,
                  output_folder: Path = None):
    """Saves specified dataframe to excel, changes filename based on inputted filename,
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
    output_config = config.get("output")

    output_dict = {}
    if output_folder is None:
        output_folder = Path.cwd()
        output_dict.update(**output_config["base"])
        output_dict.update(**output_config["excel"])
    else:
        output_folder = Path(output_folder)
    if sort_on is not None:
        df = df.sort_values(by=sort_on,
                            key=natsort_keygen()).reset_index(drop=True)
    if corrected == True:
        output_dict.update(**output_config["corrected"])
    #end ifs
    output_folder = output_folder.joinpath(*output_dict.values())
    if not output_folder.exists():
        logging.info("Creating directory %s", output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
    if split_on is not None:
        to_write = df.groupby(split_on)
        for name, frame in to_write:
            out_name = "{0}_{1}_{2}.xlsx".format(split_on, name, filename)
            out_file = output_folder.joinpath(out_name)
            logging.info("Writing out %s", out_file)
            frame.to_excel(out_name)
    else:
        out_name = "processed_{0}.xlsx".format(filename)
        out_file = output_folder.joinpath(out_name)
        logging.info("Writing out %s", out_file)
        df.to_excel(out_file)


def generate_graph_output_path(corrected: bool = False,
                               varying: bool = False,
                               brief: bool = False,
                               uniform: bool = False,
                               root: Path = None) -> PathLike:
    """Generates the output path based on configured features.

    Parameters
    ----------
    corrected : bool, optional
        Whether or not the dataframe has been corrected, by default False.
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
    PathLike
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
    if corrected == True:
        output_dict.update(**output_config["corrected"])
    if varying == True:
        if brief == True:
            output_dict.update(**output_config["briefly_varying"])
        else:
            output_dict.update(**output_config["varying"])
    else:
        output_dict.update(**output_config["non_varying"])

    output_path = output_path.joinpath(*output_dict.values())
    return output_path


def get_file_list(file_list: Tuple[PathLike, ...]) -> List[PathLike]:
    result = []
    for path in file_list:
        if path.is_dir():
            files = [
                x for x in path.iterdir()
                if x.suffix == ".csv" or x.suffix == ".xlsx"
            ]
            result.extend(files)
        else:
            result.append(path)
    return result