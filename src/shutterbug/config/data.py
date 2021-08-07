import logging
from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, validator


class ConfigData(ABC, BaseModel):
    pass


class MutableData(ConfigData):
    class Config:
        allow_mutation = True


class ImmutableData(ConfigData):
    class Config:
        allow_mutation = False
        frozen = True


class InputConfig(ImmutableData):
    required: List[str]
    coords: List[str]
    time_col_name: str
    types: List[str]


class CLIConfig(ImmutableData):
    output_folder: Path
    uniform: bool
    output_spreadsheet: bool
    correct_offset: bool
    iterations: int
    remove: str
    mag_y_scale: float
    diff_y_scale: float

    @validator("uniform")
    def mag_or_uniform(cls, uniform):
        mag_or_diff = cls.mag_y_scale or cls.diff_y_scale
        if uniform is True and mag_or_diff is True:
            logging.warning(
                "Manual y-axis scaling and uniform y-axis flag are both set, disabling uniform flag."
            )
            cls.uniform = False


class RuntimeConfig(MutableData):
    pass


class LoggingConfig(ImmutableData):
    version: int = 1  # mandatory to work
    formatters: Dict
    console_handler: Dict
    file_handler: Optional[Dict]
    root: Dict


class OutputConfig(ImmutableData):
    seaborn: Dict
    pass


class PhotometryConfig(ImmutableData):
    pass
