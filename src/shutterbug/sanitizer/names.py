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

    cleaned = []
    for name in names:
        name = clean_name(name)
        cleaned.append(name)
    return cleaned


def clean_name(name: str) -> str:
    for symbol in string.punctuation:
        name = name.strip()
        name = name.replace(symbol, "")
        name = name.lower()
    return name
