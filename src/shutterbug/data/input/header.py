from typing import List

from attr import define, field


@define
class Header:
    headers: List[str]

    def __eq__(self, other) -> bool:
        # testing set equality as this will
        # allow us to have any arbitrary
        # order of headers
        other_set = set(other.headers)
        header_set = set(self.headers)
        # self is only a subset if it contains
        # all of the other's items
        return header_set.issubset(other_set)


@define
class KnownHeader(Header):
    name: str = field()
    timeseries_names: List[str] = field()
    star_names: List[str] = field()
    star_name: str = field()

    def _get_used_indices(self, names: List[str]) -> List[int]:
        used_indices = []
        for header in names:
            header_idx = self.headers.index(header)
            used_indices.append(header_idx)
        return used_indices

    def get_timeseries_indices(self):
        return self._get_used_indices(self.timeseries_names)

    def get_star_indices(self):
        return self._get_used_indices(self.star_names)

    def get_name_index(self):
        return self.headers.index(self.star_name)

    @timeseries_names.validator
    @star_names.validator
    @star_name.validator
    def _all_in_headers(self, attribute, value):
        if not (all(header in self.headers for header in value)):
            raise ValueError(
                f"Headers in {attribute} are not in given header list {self.headers}"
            )


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
