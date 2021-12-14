from pathlib import Path
import random
import string
import pytest
import os
from typing import List
from hypothesis import given, assume
from hypothesis_fspaths import fspaths

BAD_FILENAME_CHARACTERS = {
    "<",
    ">",
    ":",
    '"',
    "/",
    "\\",
    "|",
    "?",
    "*",
    "\n",
    "\r",
    "\x0b",
    "\x0c",
    "\t",
}

TEST_FILETYPES = [
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


def useable_path_name() -> string:
    useable_characters = list(set(string.printable) - BAD_FILENAME_CHARACTERS)
    filename = "".join(
        random.choice(useable_characters) for _ in range(random.randint(1, 15))
    )
    return filename


@pytest.fixture
def existing_file_list(tmp_path: Path) -> List[Path]:
    extensions = [random.choice(TEST_FILETYPES) for _ in range(random.randint(1, 15))]
    files = []
    for ext in extensions:
        new_file = tmp_path.joinpath(useable_path_name() + ext)
        open(new_file, "a").close()
        files.append(new_file)
    yield files
    for f in files:
        os.remove(f)


@pytest.fixture(params=TEST_FILETYPES)
def useable_filename(request) -> str:
    filename = useable_path_name() + request.param
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
    out_dir = tmp_path.joinpath(useable_path_name())
    out_dir.mkdir(parents=True)
    yield tmp_path
    out_dir.rmdir


@pytest.fixture
def non_existing_dir(tmp_path: Path) -> Path:
    fake_path = tmp_path.joinpath(useable_path_name())
    return fake_path
