from __future__ import annotations
from configparser import ConfigParser

from pathlib import Path
from typing import Dict, Any, Union
from shutterbug.config.interfaces.internal import PackageConfigInterface
from attr import field, define, asdict, fields
from attr.filters import exclude


def to_folder(value: Union[str, Path]) -> Path:
    """Takes a string and returns it as a path"""
    # sanity check
    value = str(value)
    new_path = Path(value)
    if value.startswith("~\\") or value.startswith("~/"):
        new_path = new_path.expanduser()
    return new_path


class PackageBase(PackageConfigInterface):
    # as all the Package dataclasses have utility methods as the same
    # implementation, a base class makes sense
    _name = "NOTIMPLEMENTED"

    @classmethod
    def fromdict(cls, *_, **_kwargs: Dict[str, Any]):
        """Creates a configuration object from a dictionary and any arbitrary args,
        allows for any keywords or arguments to be passed in without issue"""
        attributes = fields(cls)
        field_names = []
        field_values = []
        for attrib in attributes:
            if not attrib.name.startswith("_"):
                value = _kwargs.pop(attrib.name, None)
                if value is not None:
                    field_names.append(attrib.name)
                    field_values.append(value)
        given = dict(zip(field_names, field_values))
        return cls(**given)  # type: ignore

    @property
    def asdict(self) -> Dict[str, Any]:
        """Returns the package configuration as a dictionary for writing or other use"""
        return asdict(self, filter=exclude(self._name))

    @classmethod
    def fromconfigparser(cls, parser: ConfigParser) -> PackageConfigInterface:
        """Creates package configuration from a config parser"""
        if parser.has_section(cls._name):
            return cls.fromdict(**parser[cls._name])
        return cls()


@define(kw_only=True, slots=True, auto_attribs=True)
class DataConfig(PackageBase):
    """Holds the configuration for the Data package"""

    _name = "data"

    database_path: Path = field(
        converter=to_folder, default=Path().home() / ".shutterbug" / "db.sqlite"
    )
    output_folder: Path = field(converter=to_folder, default=Path().cwd())


@define(kw_only=True, slots=True, auto_attribs=True)
class PhotometryConfig(PackageBase):
    """Holds the configuration for the Photometry package"""

    _name = "photometry"
    magnitude_limit: float = field(converter=float, default=0)
    distance_limit: float = field(converter=float, default=0)
