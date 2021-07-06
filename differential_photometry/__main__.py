import logging.config
import warnings
import importlib
from os import PathLike
from pathlib import Path

import click
import toml

import differential_photometry.config as config
import differential_photometry.plot.plot as plot
import differential_photometry.utilities.data as data
import differential_photometry.utilities.input_output as io
import differential_photometry.utilities.photometry as phot
import differential_photometry.utilities.sanitize as sanitize
import differential_photometry.utilities.timeseries as ts

# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

app_config = toml.load("config/application.toml")

importlib.reload(phot)


@click.command()
@click.argument("input_file",
                type=click.Path(file_okay=True, dir_okay=True, exists=True),
                nargs=-1,
                required=True)
@click.option("-o",
              "--output_folder",
              default=None,
              type=click.Path(file_okay=False, dir_okay=True),
              help="Root output directory for excel and graphs")
@click.option(
    "-u",
    "--uniform",
    is_flag=True,
    default=False,
    help="Flag whether the graphed dataset should share y-axis limits")
@click.option("-e",
              "--output_excel",
              is_flag=True,
              default=False,
              help="Whether to output to excel")
@click.option("-f",
              "--offset",
              is_flag=True,
              default=False,
              help="Whether to correct offset between days in the graphs")
@click.option("-i",
              "--iterations",
              type=click.INT,
              default=1,
              help="""The number of iterations that the star variation
        detection system will go through for each differential photometry run"""
              )
@click.option("-r",
              "--remove",
              type=click.STRING,
              default=None,
              help="Space separated list of names to remove from dataset")
def runner(input_file: Path, output_folder: Path, uniform: bool,
           output_excel: bool, offset: bool, iterations: int, remove: str):
    # Setup logging for verbose output
    if app_config['logging']['enabled'] == True:
        log_config = toml.load("config/logging.toml")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    # So we can have an infinite amount of folders or files to go through
    for path in input_file:
        path = Path(path)
        if path.is_dir():
            files = [
                x for x in path.iterdir()
                if x.suffix == ".csv" or x.suffix == ".xlsx"
            ]
            for data_file in files:
                logging.info("Processing file %s", data_file.stem)
                main(data_file, output_folder, uniform, output_excel, offset,
                     iterations, remove)
        else:
            logging.info("Processing file %s", path.stem)
            main(path, output_folder, uniform, output_excel, offset,
                 iterations, remove)
    logging.info("Program finished, exiting.")


def main(input_file: PathLike,
         output_folder: PathLike = None,
         uniform_y_axis: bool = False,
         output_excel: bool = False,
         correct: bool = False,
         iterations: int = 1,
         remove: str = None):

    data_directory = Path(app_config["input"]["directory"])
    file = data_directory.joinpath(input_file)

    config.filename = file

    df = io.extract(input_file)
    df = sanitize.remove_incomplete_sets(df)
    if remove is not None:
        bad_stars = remove.split(" ")
        logging.info("Attempting to remove stars: %s", bad_stars)
        try:
            star_rows = df[df["name"].isin(bad_stars)].index
            if len(star_rows) == 0:
                logging.info("No stars with specified names exist in dataset")
            else:
                df = df.drop(index=star_rows)
                logging.info("Removed stars: %s", bad_stars)
        except KeyError as e:
            logging.error("Failed to remove specified stars")
            logging.error("Error received: %s", e)
            logging.info("Continuing without star removal")

    # Find obviously varying stars
    # perform differential photometry on them
    # Drop=True to prevent index error with Pandas
    days = df.groupby([
        df["time"].dt.year, df["time"].dt.month, df["time"].dt.day
    ])  # Group by year/month/day to prevent later months from being
    # before earlier months, with an earlier day.
    # e.g. 1/7/2021 being before 22/6/2021
    star_detection_method = app_config["star_detection"]["method"]
    df = days.apply(phot.find_varying_diff_calc,
                    method=star_detection_method,
                    iterations=iterations,
                    **app_config[star_detection_method]).reset_index(drop=True)

    # Set all sets of varying stars, so that we can properly graph them
    df = data.flag_variable(df)
    # Correct for any offset found in the data
    logging.info("Total unique variable stars: %s",
                 df[df["varying"] == True]["name"].nunique())
    logging.info("Starting graphing...")

    if correct == True:
        df_corrected = ts.correct_offset(df)
        plot.plot_and_save_all(df=df_corrected,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               corrected=True,
                               output_folder=output_folder)
    else:
        plot.plot_and_save_all(df=df,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               corrected=True,
                               output_folder=output_folder)

    logging.info("Finished graphing")

    if output_excel == True:
        logging.info("Outputting processed dataset as excel...")
        if correct == True:
            io.save_to_excel(df=df_corrected,
                             filename=file.stem,
                             sort_on=["time", "name"],
                             corrected=correct,
                             output_folder=output_folder)
        else:
            io.save_to_excel(df=df,
                             filename=file.stem,
                             sort_on=["time", "name"],
                             corrected=correct,
                             output_folder=output_folder)
        logging.info("Finished excel output")


if __name__ == "__main__":
    runner()
