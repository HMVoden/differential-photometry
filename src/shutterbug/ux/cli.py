from pathlib import Path
from functools import wraps
import click
from typing import List
from shutterbug.data.interfaces.internal import DataReaderInterface
import pandas as pd


@click.group(chain=True, invoke_without_command=True)
@click.option("-d", "--debug", is_flag=True, default=False, type=click.BOOL)
def cli(debug):
    pass


@cli.command("load")
@click.option("-f", "--file", multiple=True, type=click.Path(), help="Dataset to open")
def cli_load(datasets: List[Path]):
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
