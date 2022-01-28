from typing import List
from operator import itemgetter
from attr import define, field
from attr.validators import instance_of


def strip_and_lower(strings: List[str]) -> List[str]:
    cleaned = []
    for st in strings:
        st = st.strip().lower()
        cleaned.append(st)
        strings = cleaned
    return cleaned


@define()
class Header:
    """Headers of a given file, such as a csv or excel file"""

    headers: List[str] = field(converter=strip_and_lower)

    def __eq__(self, other) -> bool:
        # testing set equality as this will
        # allow us to have any arbitrary
        # order of headers
        other_set = set(other.headers)
        header_set = set(self.headers)
        # self is only a subset if it contains
        # all of the other's items
        return header_set.issuperset(other_set)

    @headers.validator
    def _all_strings(self, _, value):
        """Ensures all headers are strings"""

        if not (all(isinstance(item, str) for item in value)):
            raise ValueError("All headers must be strings")


@define()
class KnownHeader(Header):
    """Manual definition of a known header, to be used for comparison and for
    convenience functions to get necessary indices"""

    header_origin: str = field(validator=instance_of(str))
    timeseries_names: List[str] = field(converter=strip_and_lower)
    star_data: List[str] = field(converter=strip_and_lower)
    star_name: str = field(validator=instance_of(str), converter=(lambda x: x.lower()))

    def _get_used_indices(self, names: List[str]) -> List[int]:
        """Given a list of names returns all the header indices that match the names

        Parameters
        ----------
        names : List[str]
            List of names, from a header list

        Returns
        -------
        List[int]
            Indices of the names provided

        """
        headers = self.headers
        used_indices = []
        for header in names:
            header_idx = headers.index(header)
            used_indices.append(header_idx)
        return used_indices

    def _indices_getters(self, names: List[str]) -> itemgetter:
        indices = self._get_used_indices(names)
        return itemgetter(*indices)

    @property
    def timeseries_getters(self) -> itemgetter:
        """Itemgetter for all timeseries information columns in the header"""

        return self._indices_getters(self.timeseries_names)

    @property
    def star_getters(self) -> itemgetter:
        """Itemgetter for all star data information columns in the header"""

        return self._indices_getters(self.star_data)

    @property
    def name_index(self) -> int:
        """Index of the star names column"""
        headers = self.headers
        star_name = self.star_name.lower()
        return headers.index(star_name)

    @timeseries_names.validator
    @star_data.validator
    @star_name.validator
    def _all_in_headers(self, _, value):
        if type(value) == str:
            if value not in self.headers:
                raise ValueError(
                    f"Header '{value}' is not in given header list {self.headers}"
                )
        elif not (all(header in self.headers for header in value)):
            raise ValueError(
                f"Headers '{', '.join(value)}' are not in given header list {self.headers}"
            )

    @timeseries_names.validator
    @star_data.validator
    def _all_strings(self, _, value):
        if not (all(isinstance(item, str) for item in value)):
            raise ValueError("All headers must be strings")


KNOWN_HEADERS = [
    KnownHeader(
        header_origin="Mira",
        headers=[
            "Image",
            "Name",
            "Mag",
            "Error",
            "X",
            "Y",
            "Date",
            "Time",
            "JD",
            "ExpTime",
        ],
        timeseries_names=["JD", "Mag", "Error"],
        star_data=["Name", "X", "Y"],
        star_name="Name",
    )
]
