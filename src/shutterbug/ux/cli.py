import logging
from functools import wraps
from pathlib import Path
from typing import List

import click
from click.core import Context
from shutterbug.application import (initialize_application, make_dataset,
                                    make_file_loader, make_reader_writer)
from shutterbug.data import Dataset, DBReader, DBWriter
from shutterbug.data.file import FileInput
from shutterbug.data.interfaces.internal import Reader
from shutterbug.data_nodes import CSVSaveNode, GraphSaveNode, StoreNode
from shutterbug.process_nodes import DifferentialNode, VariabilityNode
from shutterbug.ux.progress_bars import ProgressBarManager


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
    help="Datasets to load",
)
@click.pass_context
def load(context: Context, files: List[Path]):
    pass


@cli.command("process")
def process(reader: Reader):
    pass


@click.command("save")
@click.option("-o", "--out-folder", type=click.Path())
@click.option("-g" "--graph", type=click.BOOL, is_flag=True, default=True)
@click.option("-c" "--csv", type=click.BOOL, is_flag=True, default=True)
@click.option("-v" "--variable", type=click.BOOL, is_flag=True, default=False)
def cli_save(
    dataset: Dataset, out_folder: Path, graph: bool, csv: bool, variable: bool
):
    pass
