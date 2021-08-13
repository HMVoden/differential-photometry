import logging
from pathlib import Path

import xarray as xr
from natsort import natsort_keygen


def save_to_csv(
    ds: xr.Dataset,
    filename: str,
    output_flag: bool,
    output_config: dict,
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
        df = df.sort_values(["time", "star"], key=natsort_keygen())
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
        logging.info("Finished csv output")
    return ds
