import re
import string
from typing import List


def clean_names(names: List[str]) -> List[str]:
    """Takes a list of names which are returned clean

    Removes parenthesis, underscores, strips extra whitespace and makes the
    headers lowercase.

    Parameters
    ----------
    names : List[str]
        List of names to be cleaned

    Returns
    -------
    List[str]
        Cleaned list of names

    """
    remove = string.punctuation
    for name in names:
        name = re.sub(f"[{remove}]*", "", name.strip().lower())
    return names
