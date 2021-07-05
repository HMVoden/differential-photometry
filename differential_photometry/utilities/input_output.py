import logging
from os import PathLike
from pathlib import Path, PurePath
from typing import List

import numpy as np
import pandas as pd
import toml
import differential_photometry.config as config
from differential_photometry.utilities.sanitize import clean_stars_data
from natsort import natsort_keygen

output_config = toml.load("config/output.toml")


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
        Dataframe containing only required columns, trimmed and made usable
    """
    data_path = PurePath(filename)
    if (data_path.suffix == ".xlsx"
        ):  # This way we can ignore if it's a csv or excel file
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    df.columns = (df.columns.str.strip().str.lower().str.replace(
        " ", "_").str.replace("(", "_").str.replace(")", "").str.replace(
            "<", "").str.replace(">", ""))
    # Cleanup of headers, could be made more succinct with a simple REGEX
    desired_column_names = np.array(
        ["obj", "name", "mag", "error", "x", "y", "jd"])
    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this script.
    extracted_column_names = df.columns
    # Finds common column names
    intersection = np.intersect1d(desired_column_names, extracted_column_names)
    df = clean_stars_data(df[intersection])
    # names index for future use
    df.index.name = "index"
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
    output_dict = {}
    if output_folder is None:
        output_folder = Path.cwd()
        output_dict.update(**output_config["output"]["base"])
        output_dict.update(**output_config["output"]["excel"])
    else:
        output_folder = Path(output_folder)
    if sort_on is not None:
        df = df.sort_values(by=sort_on, key=natsort_keygen())
    if corrected == True:
        output_dict.update(**output_config["output"]["corrected"])
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
                               split: bool = False,
                               uniform: bool = False,
                               root: Path = None) -> PathLike:
    """Generates the output path based on configured features.

    Parameters
    ----------
    corrected : bool, optional
        Whether or not the dataframe has been corrected, by default False.
    varying : bool, optional
        Whether or not the dataframe data is varying, by default False.
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
    output_dict = {}
    if root is None:
        output_path = Path.cwd()  # current directory of script
    else:
        output_path = root
    output_dict.update(**output_config["output"]["base"])
    dataset = config.filename
    output_dict["dataset"] = dataset.stem.split("_")[0]
    output_dict["input_filename"] = dataset.stem
    if uniform == True:
        output_dict.update(**output_config["output"]["uniform"])
    if corrected == True:
        output_dict.update(**output_config["output"]["corrected"])
    if varying == True:
        output_dict.update(**output_config["output"]["varying"])
    elif split == True:
        output_dict.update(**output_config["output"]["non_varying"])

    output_path = output_path.joinpath(*output_dict.values())
    return output_path
