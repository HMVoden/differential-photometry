from __future__ import annotations
from configparser import ConfigParser

from pathlib import Path
from typing import Dict, Any
from shutterbug.config.interfaces.internal import PackageConfigInterface
from attr import field, define, asdict


def path_from_string(value: str) -> Path:
    """Takes a string and returns it as a path"""
    # sanity check
    value = str(value)
    new_path = Path(value)
    if value.startswith("~\\"):
        new_path = new_path.expanduser()
    return new_path


class PackageBase(PackageConfigInterface):
    # as all the Package dataclasses have asdict as the same implementation,
    # a base class makes sense
    _name = "NOTIMPLEMENTED"

    @classmethod
    def fromdict(cls, *_, **_kwargs):
        raise NotImplementedError

    @property
    def asdict(self) -> Dict[str, Any]:
        """Returns the package configuration as a dictionary for writing or other use"""
        return asdict(self)

    @classmethod
    def fromconfigparser(cls, parser: ConfigParser) -> PackageConfigInterface:
        """Creates package configuration from a config parser"""
        if parser.has_section(cls._name):
            return cls.fromdict(parser.get(section=cls._name))
        return cls()


@define(kw_only=True, slots=True)
class DataConfig(PackageBase):
    """Holds the configuration for the Data package"""

    _name = "data"

    database: Path = field(
        converter=path_from_string, default=Path().home() / ".shutterbug" / "db.sqlite"
    )
    output_folder: Path = field(converter=path_from_string, default=Path().cwd())

    @classmethod
    def fromdict(cls, *_, **kwargs: Dict[str, Any]) -> DataConfig:
        """Creates a configuration object from a dictionary and any arbitrary args,
        allows for any keywords or arguments to be passed in without issue"""

        database = kwargs.pop("database", None)
        output_folder = kwargs.pop("output_folder", None)
        return cls(database=database, output_folder=output_folder)  # type: ignore

    @property
    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


@define(kw_only=True, slots=True)
class PhotometryConfig(PackageBase):
    """Holds the configuration for the Photometry package"""

    _name = "photometry"
    magnitude_limit: float = field(converter=float, default=0)
    distance_limit: float = field(converter=float, default=0)

    @classmethod
    def fromdict(cls, *_, **kwargs: Dict[str, Any]) -> PhotometryConfig:
        """Creates a configuration object from a dictionary and any arbitrary args,
        allows for any keywords or arguments to be passed in without issue"""
        mag_lim = kwargs.pop("magnitude_limit", None)
        dis_lim = kwargs.pop("distance_limit", None)
        return cls(magnitude_limit=mag_lim, distance_limit=dis_lim)  # type: ignore

    @property
    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


@define(kw_only=True, slots=True)
class VariabilityConfig(PackageBase):
    """Holds the configuration for the Variability package"""

    _name = "variability"

    @classmethod
    def fromdict(cls, *_, **kwargs: Dict[str, Any]) -> VariabilityConfig:
        """Creates a configuration object from a dictionary and any arbitrary args,
        allows for any keywords or arguments to be passed in without issue"""

        return cls()

    @property
    def asdict(self) -> Dict[str, Any]:
        return asdict(self)
