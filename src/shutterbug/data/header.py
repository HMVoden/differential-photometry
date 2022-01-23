from typing import List
from operator import itemgetter
from attr import define, field
from attr.validators import instance_of


@define(slots=True, frozen=True)
class Header:
    """Headers of a given file, such as a csv or excel file"""

    headers: List[str] = field()

    def __eq__(self, other) -> bool:
        # testing set equality as this will
        # allow us to have any arbitrary
        # order of headers
        other_set = set(other.headers)
        header_set = set(self.headers)
        # self is only a subset if it contains
        # all of the other's items
        return header_set.issubset(other_set) and other_set.issubset(header_set)

    @headers.validator
    def _all_strings(self, _, value):
        """Ensures all headers are strings"""

        if not (all(isinstance(item, str) for item in value)):
            raise ValueError("All headers must be strings")


@define(slots=True, frozen=True)
class KnownHeader(Header):
    """Manual definition of a known header, to be used for comparison and for
    convenience functions to get necessary indices"""

    name: str = field(validator=instance_of(str))
    timeseries_names: List[str] = field()
    star_names: List[str] = field()
    star_name: str = field(validator=instance_of(str))

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

        used_indices = []
        for header in names:
            header_idx = self.headers.index(header)
            used_indices.append(header_idx)
        return used_indices

    def _indices_getters(self, names: List[str]) -> itemgetter[str]:
        indices = self._get_used_indices(names)
        return itemgetter(*indices)

    @property
    def timeseries_getters(self) -> itemgetter[str]:
        """Itemgetter for all timeseries information columns in the header"""

        return self._indices_getters(self.timeseries_names)

    @property
    def star_getters(self) -> itemgetter[str]:
        """Itemgetter for all star data information columns in the header"""

        return self._indices_getters(self.star_names)

    @property
    def name_index(self) -> int:
        """Index of the star names column"""
        return self.headers.index(self.star_name)

    @timeseries_names.validator
    @star_names.validator
    @star_name.validator
    def _all_in_headers(self, attribute, value):
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
    @star_names.validator
    def _all_strings(self, attribute, value):
        if not (all(isinstance(item, str) for item in value)):
            raise ValueError("All headers must be strings")


KNOWN_HEADERS = [
    KnownHeader(
        name="Mira",
        headers=[
            "#",
            "Image",
            "Index",
            "Name",
            "Mag",
            "Std?",
            "Error",
            "Error(T)",
            "X",
            "Y",
            "Column",
            "Row",
            "Backgr",
            "S/N",
            "Mag Std",
            "Residual",
            "Net Count",
            "Filter",
            "Date",
            "Time",
            "JD",
            "Airmass",
            "ExpTime",
            "Weight",
            "Notes",
        ],
        timeseries_names=["JD", "Mag", "Error"],
        star_names=["Name", "X", "Y"],
        star_name="Name",
    )
]
