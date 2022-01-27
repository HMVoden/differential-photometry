from pathlib import Path
from functools import wraps
import click
import logging
from typing import List

from click.core import Context
from shutterbug.data.interfaces.internal import DataReaderInterface
from shutterbug.data.file import FileInput
from shutterbug.data.db.writer import DBWriter
from shutterbug.data.db.reader import DBReader
import pandas as pd
from shutterbug.ux.progress_bars import ProgressBarManager
from shutterbug.init import initialize_logging, initialize_application


@click.group(chain=True, invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def cli(context: Context, debug: bool):
    initialize_logging(debug=debug)
    config, engine = initialize_application()
    logging.info("Initializing application")
    context.obj = {}
    context.obj["pbar_manager"] = ProgressBarManager()


@cli.command("load")
@click.option(
    "-f",
    "--file",
    "files",
    multiple=True,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=True, readable=True, path_type=Path
    ),
    help="Dataset to load",
)
@click.pass_context
def cli_load(context: Context, files: List[Path]):
    pbar_manager = context.obj["pbar_manager"]
    for file_path in files:
        dataset = FileInput(file_path)
        with pbar_manager.new(
            desc="Iterating Datasets", unit="dataset", total=len(dataset)
        ) as pbar1:
            for loader in dataset:
                with pbar_manager.new(
                    desc="Loading stars",
                    unit="star",
                    total=len(loader),
                    stage="Processing",
                ) as pbar2:
                    for star in loader:
                        pbar2.update()

                pbar1.update()


@cli.command("process")
def cli_process(reader: DataReaderInterface):
    pass


@click.command("save")
@click.option("-o", "--out-folder", type=click.Path())
@click.option("-g" "--graph", type=click.BOOL, is_flag=True, default=True)
@click.option("-c" "--csv", type=click.BOOL, is_flag=True, default=True)
def cli_save(frame: pd.DataFrame, out_folder: Path, graph: bool, csv: bool):
    pass
