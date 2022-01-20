from pathlib import Path

import click


@click.command()
@click.argument(
    "input_data",
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
    "--output-spreadsheet",
    is_flag=True,
    default=False,
    help="Whether to output to a spreadsheet",
)
@click.option(
    "-f",
    "--correct-offset",
    is_flag=True,
    default=False,
    help="Whether to correct offset between days in the graphs",
)
@click.option(
    "-i",
    "--iterations",
    type=click.INT,
    default=2,
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
def cli(input_data, **cli_settings):
    pass
