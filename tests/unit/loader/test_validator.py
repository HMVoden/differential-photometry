from pathlib import Path
import random
import string
import pytest
import os
from shutterbug.file_loader.validator.validators.is_file import IsFileValidator
from shutterbug.file_loader.validator.validators.exists import ExistsValidator
from shutterbug.file_loader.validator.validators.is_dir import IsDirectoryValidator
from hypothesis import given, assume
from hypothesis_fspaths import fspaths


@pytest.fixture
def useable_path_name():
    useable_characters = string.ascii_letters.join(string.digits)
    filename = "".join(
        random.choice(useable_characters) for _ in range(random.randint(1, 15))
    )
    return filename


@pytest.fixture(
    params=[
        ".csv",
        ".xlxs",
        ".xlsx",
        ".xls",
        ".xlsm",
        ".odf",
        ".cs",
        "csv",
        ".hd5",
        ".nc",
        ".ods",
        ".parquet",
        ".ods",
        ".txt",
        ".steve",
        "",
    ]
)
def useable_filename(request, useable_path_name: str) -> str:
    filename = useable_path_name + request.param
    return filename


@pytest.fixture
def existing_file(tmp_path: Path, useable_filename: string) -> Path:
    out_file = tmp_path.joinpath(useable_filename)
    open(out_file, "a").close()
    yield out_file
    os.remove(out_file)


@pytest.fixture
def non_existing_file(tmp_path: Path, useable_filename: string) -> Path:
    out_file = tmp_path.joinpath(useable_filename)
    yield out_file


@pytest.fixture
def existing_dir(tmp_path: Path) -> Path:
    yield tmp_path


@pytest.fixture
def non_existing_dir(tmp_path: Path, useable_path_name) -> Path:
    fake_path = tmp_path.joinpath(useable_path_name)
    return fake_path


@pytest.mark.parametrize(
    "validator, expected",
    [
        (IsFileValidator(), True),
        (ExistsValidator(), True),
        (IsDirectoryValidator(), False),
    ],
)
def test_existing_file(existing_file, validator, expected):
    assert validator.validate(existing_file) is expected


@pytest.mark.parametrize(
    "validator, expected",
    [
        (IsFileValidator(), False),
        (ExistsValidator(), True),
        (IsDirectoryValidator(), True),
    ],
)
def test_existing_dir(existing_dir, validator, expected):
    assert validator.validate(existing_dir) is expected


@pytest.mark.parametrize(
    "validator, expected",
    [
        (IsFileValidator(), False),
        (ExistsValidator(), False),
        (IsDirectoryValidator(), False),
    ],
)
def test_non_existing_dir(non_existing_dir, validator, expected):
    assert validator.validate(non_existing_dir) is expected


@pytest.mark.parametrize(
    "validator, expected",
    [
        (IsFileValidator(), False),
        (ExistsValidator(), False),
        (IsDirectoryValidator(), False),
    ],
)
def test_non_existing_file(non_existing_file, validator, expected):
    assert validator.validate(non_existing_file) is expected
