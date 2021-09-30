from typing import List, Optional, Union

import pandas as pd
import xarray as xr


def sanitize(
    frame: Union[pd.DataFrame, xr.Dataset],
    primary_variables: List[str],
    numeric_variables: Optional[List[str]] = None,
    discard_variables: Optional[List[str]] = None,
    keep_variables: Optional[List[str]] = None,
    keep_duplicates: Optional[str] = "first",
) -> Union[pd.Dataframe, xr.Dataset]:
    """Takes a pandas dataframe or xarray dataset, cleans all headers/variable names by stripping out non-alphabetic characters except for "_" which is used as a spacer between words, if necessary. Ensures that data is in the proper format and is clean by removing any duplicates according to settings and removing any entries with NaN.


    Parameters
    ----------
    frame : Union[pd.DataFrame, xr.Dataset]
        A dataset to be cleaned
    primary_variables : List[str]
        A list of the variable names that are used to determine if there are duplicate entries and how to remove entries if NaN entries are found in numeric variables.
    numeric_variables : Optional[List[str]]
        A list of variable names in the dataset that should be numeric
    discard_variables : Optional[List[str]]
        A list of variable names to discard. If neither discard or keep
        variables is set, no variables are dropped.
    keep_variables : Optional[List[str]]
        A list of variable names to keep. If neither discard or keep variables
        is set, no variables are dropped.
    keep_duplicates : Optional[str]
        Can be either "first", "last" or None, if duplicates are found then this setting determines which ones are
        kept, if any.

    Returns
    -------
    Union[pd.Dataframe, xr.Dataset]
        A clean dataset

    """
    pass
