from pathlib import Path
from functools import wraps
import click
import logging
from typing import List
from shutterbug.data.interfaces.internal import DataReaderInterface
from shutterbug.data.file import FileInput
from shutterbug.data.db.writer import DBWriter
from shutterbug.data.db.reader import DBReader
import pandas as pd


@click.group(chain=True, invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, default=False, type=click.BOOL)
def cli(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


@cli.command("load")
@click.option(
    "-f",
    "--file",
    "files",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, path_type=Path
    ),
    help="Dataset to open",
)
def cli_load(files: List[Path]):
    for file_path in files:
        dataset = FileInput(file_path)
        for loader in dataset:
            for star in loader:
                pass


@cli.command("process")
def cli_process(reader: DataReaderInterface):
    pass


@click.command("save")
@click.option("-o", "--out-folder", type=click.Path())
@click.option("-g" "--graph", type=click.BOOL, is_flag=True, default=True)
@click.option("-c" "--csv", type=click.BOOL, is_flag=True, default=True)
def cli_save(frame: pd.DataFrame, out_folder: Path, graph: bool, csv: bool):
    pass
