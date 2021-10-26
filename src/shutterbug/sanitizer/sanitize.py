from typing import List, Optional, Union

import pandas as pd
import xarray as xr
from shutterbug.sanitizer.pandas_sanitizer import PandasSanitizer
from shutterbug.sanitizer.xarray_sanitizer import XarraySanitizer


def sanitize(
    frame: Union[pd.DataFrame, xr.Dataset],
    primary_variables: List[str],
    numeric_variables: Optional[List[str]] = None,
    discard_variables: Optional[List[str]] = None,
    keep_variables: Optional[List[str]] = None,
    keep_duplicates: Optional[str] = "first",
) -> Union[pd.DataFrame, xr.Dataset]:
    """Takes a pandas dataframe or xarray dataset, cleans all headers/variable names by stripping out non-alphabetic characters and making headers lowercase, if necessary. Ensures that numeric data is in the proper format and is clean by removing any duplicates according to settings and removing any entries with NaN.


    Parameters
    ----------
    frame : Union[pd.DataFrame, xr.Dataset]
        A dataset to be cleaned
    primary_variables : List[str]
        A list of the variable names that are used to determine if there are duplicate entries and how to remove entries if NaN entries are found in numeric variables.
    numeric_variables : Optional[List[str]]
        A list of variable names in the dataset that should be numeric. Default None
    discard_variables : Optional[List[str]]
        A list of variable names to discard. If neither discard or keep
        variables is set, no variables are dropped. Default None
    keep_variables : Optional[List[str]]
        A list of variable names to keep. If neither discard or keep variables
        is set, no variables are dropped. Default None
    keep_duplicates : Optional[str]
        Can be either "first", "last" or False, if duplicates are found then this setting determines which ones are
        kept, if any. Default "first"

    Returns
    -------
    Union[pd.Dataframe, xr.Dataset]
        A clean dataset of input type

    """
    duplicate_settings = ["first", "last", False]
    if keep_variables and discard_variables:
        raise ValueError(
            "Cannot keep and discard variables, either keep or discard can be set"
        )
    if keep_duplicates not in duplicate_settings:
        raise ValueError(
            f"keep_duplicates must be one of the following settings: {' '.join(duplicate_settings)}, was {keep_duplicates}"
        )
    if len(primary_variables) < 1:
        raise ValueError("Must have primary variables for deduplication")
    if isinstance(frame, xr.Dataset):
        sanitizer = XarraySanitizer()
    elif isinstance(frame, pd.DataFrame):
        sanitizer = PandasSanitizer()
    else:
        raise ValueError(f"Unable to sanitize dataframe of type {type(frame)}")
    return sanitizer.sanitize(
        frame=frame,
        primary_variables=primary_variables,
        numeric_variables=numeric_variables,
        discard_variables=discard_variables,
        keep_variables=keep_variables,
        keep_duplicates=keep_duplicates,
    )
