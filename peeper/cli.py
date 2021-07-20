import logging.config
import warnings
from pathlib import Path

import click

import peeper.progress_bars as bars
import peeper.runner as runner
import peeper.data.input_output as io
import peeper.data.sanitize as sanitize

from pandas.errors import DtypeWarning


# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=DtypeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@click.command()
@click.argument(
    "input_file",
    type=click.Path(file_okay=True, dir_okay=True, exists=True, path_type=Path),
    nargs=-1,
    required=True,
)
@click.option(
    "-o",
    "--output_folder",
    default=None,
    type=click.Path(file_okay=False, dir_okay=True),
    help="Root output directory for excel and graph output",
)
@click.option(
    "-u",
    "--uniform",
    is_flag=True,
    default=False,
    help="Flag whether the graphed dataset should share y-axis limits",
)
@click.option(
    "-e",
    "--output_excel",
    is_flag=True,
    default=False,
    help="Whether to output to excel",
)
@click.option(
    "-f",
    "--offset",
    is_flag=True,
    default=False,
    help="Whether to correct offset between days in the graphs",
)
@click.option(
    "-i",
    "--iterations",
    type=click.INT,
    default=1,
    help="""The number of iterations that the star variation
        detection system will go through for each differential photometry run""",
)
@click.option(
    "-r",
    "--remove",
    type=click.STRING,
    default=None,
    help="Space or comma separated list of names to remove from dataset",
)
@click.option(
    "-m",
    "--mag_y_scale",
    type=click.FLOAT,
    default=None,
    help="""Sets the magnitude y-scale to have this value above and below the median
              of any dataset when plotted. OVERRIDES UNIFORM""",
)
@click.option(
    "-d",
    "--diff_y_scale",
    type=click.FLOAT,
    default=None,
    help="""Sets the differential magnitude y-scale to have this value above and below the median
              of any dataset when plotted. OVERRIDES UNIFORM""",
)
def cli(
    input_file: Path,
    output_folder: Path,
    uniform: bool,
    output_excel: bool,
    offset: bool,
    iterations: int,
    remove: str,
    mag_y_scale: float,
    diff_y_scale: float,
):
    remove = sanitize.to_remove_to_list(remove)
    runner.initialize(
        output_folder=output_folder,
        uniform=uniform,
        output_excel=output_excel,
        offset=offset,
        iterations=iterations,
        remove=remove,
        mag_y_scale=mag_y_scale,
        diff_y_scale=diff_y_scale,
    )

    manager = bars.manager
    status = bars.status

    files = io.get_file_list(input_file)
    pbar = manager.counter(
        desc="Processing datasets", unit="Datasets", total=len(files)
    )

    for data_file in files:
        status.update(demo="Processing file")
        logging.info("Processing file %s", data_file.stem)
        runner.run(input_file=data_file)
        bars.close_progress_bars()
        pbar.update()
    status.update(demo="Finished")
    pbar.close()
    runner.teardown()
    logging.info("Program finished, exiting.")
