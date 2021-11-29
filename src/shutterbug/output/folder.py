from pathlib import Path
from typing import Dict


def generate_graph_output_path(
    filename: str,
    output_config: Dict,
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
    output_dict = {}
    if root is None:
        output_path = Path.cwd()  # current directory of script
    else:
        output_path = root
    output_dict.update(**output_config["base"])
    output_dict["dataset"] = filename.split("_")[0]
    output_dict["input_filename"] = filename
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
