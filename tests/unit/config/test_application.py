from pathlib import Path
from shutterbug.config.application import (
    ApplicationConfig,
    make_data_folder,
    default_config,
)
from shutterbug.config.packages import PhotometryConfig, DataConfig
import pytest
import tempfile


def test_defaults():
    defaults = default_config
    d_pho = PhotometryConfig()
    d_dat = DataConfig()
    assert defaults._data == d_dat
    assert defaults._photometry == d_pho


def test_data_folder():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)
        data_path = make_data_folder(path)
        assert data_path == path
        assert data_path.exists()


def test_non_existant_folder():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d)
        path.rmdir()
        data_path = make_data_folder(path)
        assert path == data_path
        assert data_path.exists()
