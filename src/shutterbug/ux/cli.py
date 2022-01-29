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
from shutterbug.init import initialize_application


@click.group(chain=True, invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, default=False, type=click.BOOL)
@click.pass_context
def cli(context: Context, debug: bool):
    config, engine = initialize_application(debug=debug)
    context.obj = {}
    context.obj["pbar_manager"] = ProgressBarManager()
    context.obj["config"] = config
    context.obj["database"] = engine


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
    config = context.obj["config"]
    database = context.obj["database"]
    for file_path in files:
        writer = DBWriter(dataset=file_path.stem, engine=database)
        dataset = FileInput(file_path)
        with pbar_manager.new(
            desc="Iterating Datasets", unit="dataset", total=len(dataset)
        ) as pbar1:
            for loader in dataset:
                with pbar_manager.new(
                    desc="Loading",
                    unit="star",
                    total=len(loader),
                    stage="Loading into database",
                ) as pbar2:
                    for star in loader:
                        writer.write(star)
                        pbar2.update()
                with pbar_manager.new(
                    desc="Photometry",
                    unit="star",
                    total=len(loader),
                    stage="Photometry",
                ) as pbar3:
                    reader = DBReader(dataset=file_path.stem, engine=database)
                    for star in reader.all:
                        pbar3.update()
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
