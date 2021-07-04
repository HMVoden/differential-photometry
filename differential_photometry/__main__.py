# %%
import importlib
import logging.config
import warnings
from os import PathLike
from pathlib import Path

import click
import toml
from tqdm import tqdm

import differential_photometry.config as config
import differential_photometry.plot.plot as plot
import differential_photometry.utilities.data as data
import differential_photometry.utilities.input_output as io
import differential_photometry.utilities.photometry as phot
import differential_photometry.utilities.sanitize as sanitize
import differential_photometry.utilities.timeseries as ts

# from feets import ExtractorWarning

# import differential_photometry.config as config

# importlib.reload(phot)
# importlib.reload(sanitize)
# importlib.reload(io)
# importlib.reload(ts)
# importlib.reload(plot)
# importlib.reload(data)

# CONSTANTS ============================================================================
# FILENAME = 'data.csv'
# FILENAME = "M3_raw01_Photometry25-47-59.csv"
# FILENAME = "M3_2nights_rawPhotometry.csv"
# FILENAME = 'M3_night_1.xlsx'
# FILENAME = 'M3_night_2.xlsx'
# FILENAME = "M92_rawPhotometry_v01_total.csv"
# FILENAME = 'M92_rawPhotometry_v02_total.csv'

# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

app_config = toml.load("config/application.toml")
tqdm.pandas(leave=False)


@click.command()
@click.argument("input_file",
                type=click.Path(file_okay=True, dir_okay=True, exists=True),
                nargs=-1,
                required=True)
@click.option("--output_folder",
              default=app_config["input"]["directory"],
              type=click.Path(file_okay=False, dir_okay=True, exists=False),
              help="Root output directory for excel and graphs")
@click.option(
    "--uniform_y_axis",
    default=False,
    help="Flag whether the graphed dataset should share y-axis limits")
@click.option("--output_excel",
              default=False,
              help="Whether to output to excel")
@click.option("--correct",
              default=False,
              help="Whether to correct offset between days in the graphs")
def runner(input_file: Path, output_folder: Path, uniform_y_axis: bool,
           output_excel: bool, correct: bool):

    if app_config['logging']['enabled'] == True:
        log_config = toml.load("config/logging.toml")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    for path in input_file:
        path = Path(path)
        if path.is_dir():
            files = [
                x for x in path.iterdir()
                if x.suffix == ".csv" or x.suffix == ".xlsx"
            ]
            for data_file in files:
                logging.info("Processing file %s", data_file.stem)
                main(data_file, output_folder, uniform_y_axis, output_excel,
                     correct)
        else:
            logging.info("Processing file %s", path.stem)
            main(path, output_folder, uniform_y_axis, output_excel, correct)


def main(input_file: PathLike,
         output_folder: PathLike = None,
         uniform_y_axis: bool = False,
         output_excel: bool = False,
         correct: bool = False):

    data_directory = Path(app_config["input"]["directory"])
    file = data_directory.joinpath(input_file)

    config.filename = file

    df = io.extract(input_file)

    df = sanitize.remove_incomplete_sets(df)

    days = df.groupby("d_m_y")

    # Find obviously varying stars
    # perform differential photometry on them
    # Drop=True to prevent index error with Pandas
    star_detection_method = app_config["star_detection"]["method"]
    df = days.apply(phot.find_varying_diff_calc,
                    method=star_detection_method,
                    **app_config[star_detection_method]).reset_index(drop=True)

    # Set all sets of varying stars, so that we can properly graph them
    df = data.flag_variable(df)
    # Correct for any offset found in the data

    logging.info("Starting graphing")
    if correct == True:
        df_corrected = ts.correct_offset(df)
        plot.plot_and_save_all(df=df_corrected,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               output_folder=output_folder)
    else:
        plot.plot_and_save_all(df=df,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               output_folder=output_folder)

    if output_excel == True:
        io.save_to_excel(df=df,
                         filename=file.stem,
                         sort_on=["time", "name"],
                         output_folder=output_folder)
    logging.info("Finished graphing")


if __name__ == "__main__":
    runner()
