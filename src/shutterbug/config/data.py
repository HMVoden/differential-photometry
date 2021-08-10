import logging
from abc import ABC
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, validator
from pydantic.class_validators import root_validator


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
    mag_y_scale: Optional[float]
    diff_y_scale: Optional[float]
    input_data: List[Path]
    output_folder: Optional[Path]
    output_spreadsheet: Optional[bool]
    correct_offset: Optional[bool]
    iterations: int
    remove: Optional[List[str]]
    uniform: Optional[bool]

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

    @root_validator
    def mag_or_uniform(cls, values) -> Optional[bool]:
        uniform = values.get("uniform")
        mag_y_scale = values.get("mag_y_scale")
        diff_y_scale = values.get("diff_y_scale")
        mag_or_diff = mag_y_scale or diff_y_scale
        if uniform is True and mag_or_diff is True:
            logging.warning(
                "Manual y-axis scaling and uniform y-axis flag are both set, disabling uniform flag."
            )
            cls.uniform = False
        return values


class RuntimeConfig(MutableData):
    pass


class LoggingConfig(ImmutableData):
    version: int = 1  # mandatory to work
    formatters: Dict
    handlers: Dict
    root: Dict


class OutputConfig(ImmutableData):
    seaborn: Dict
    pass


class PhotometryConfig(ImmutableData):
    detection_method: str
    p_value: float
    clip: bool
    null: str
