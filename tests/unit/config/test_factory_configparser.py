from shutterbug.config.factory_configparser import from_file, data_folder, to_file
from shutterbug.config.application import (
    ApplicationConfig,
    default_config,
    make_data_folder,
)
import pytest
import tempfile
import configparser
from pathlib import Path

from shutterbug.config.packages import DataConfig, PhotometryConfig


def test_empty_path():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "test.ini"
        config = from_file(path)
        assert config == default_config


def test_to_file():
    with tempfile.NamedTemporaryFile(mode="r+", suffix=".ini") as f:
        result = to_file(file=Path(f.name), config=default_config)
        parser = configparser.ConfigParser()
        parser.read_file(f.readlines(), source=f.name)
        in_file = ApplicationConfig(
            photometry=PhotometryConfig.fromconfigparser(parser),
            data=DataConfig.fromconfigparser(parser),
        )
        assert in_file == default_config
        assert result == True


def test_data_folder():
    folder = data_folder()
    assert folder == make_data_folder()
