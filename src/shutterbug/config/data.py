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


class DataConfig(ImmutableData):
    required: List[str]
    coords: List[str]
    time_col_name: str
    reader: Dict


class CLIConfig(ImmutableData):
    input_data: List[Path]
    output_folder: Path
    uniform: bool
    output_spreadsheet: bool
    correct_offset: bool
    iterations: int
    remove: List[str]
    mag_y_scale: float
    diff_y_scale: float

    @validator("input_data")
    def make_file_list(cls, input_data: List[Path]) -> List[Path]:
        result = []
        for path in input_data:
            if path.is_dir():
                files = [x for x in path.iterdir() if x.is_file()]
                result.extend(files)
            else:
                result.append(path)
        return result

    @validator("remove")
    def split_str(cls, remove: str) -> List[str]:
        if remove is not None:
            if "," in remove:
                remove = remove.replace(" ", "")
                result = remove.split(",")
            else:
                result = remove.split(" ")
            return result
        return [""]

    @validator("uniform", pre=True)
    def mag_or_uniform(cls, uniform: bool) -> bool:
        mag_or_diff = cls.mag_y_scale or cls.diff_y_scale
        if uniform is True and mag_or_diff is True:
            logging.warning(
                "Manual y-axis scaling and uniform y-axis flag are both set, disabling uniform flag."
            )
            return False
        return uniform


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
