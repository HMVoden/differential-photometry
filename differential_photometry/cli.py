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
import differential_photometry.utilities.progress_bars as bars

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
              help="Root output directory for excel and graph output")
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
@click.option(
    "-r",
    "--remove",
    type=click.STRING,
    default=None,
    help="Space or comma separated list of names to remove from dataset")
@click.option(
    "-my",
    "--mag_y_scale",
    type=click.FLOAT,
    default=None,
    help=
    """Sets the magnitude y-scale to have this value above and below the median
              of any dataset when plotted. OVERRIDES UNIFORM""")
@click.option(
    "-dy",
    "--diff_y_scale",
    type=click.FLOAT,
    default=None,
    help=
    """Sets the differential magnitude y-scale to have this value above and below the median
              of any dataset when plotted. OVERRIDES UNIFORM""")
def runner(input_file: Path, output_folder: Path, uniform: bool,
           output_excel: bool, offset: bool, iterations: int, remove: str,
           mag_y_scale: float, diff_y_scale: float):
    bars.init_progress_bars()
    manager = config.pbar_man
    status = config.pbar_status
    # Setup logging for verbose output
    if app_config['logging']['enabled'] == True:
        log_config = toml.load("config/logging.toml")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    inputted_pbar = manager.counter(desc="Input files or paths",
                                    unit="inputs",
                                    total=len(input_file),
                                    color="green")
    pbar = manager.counter(desc='Processing datasets',
                           unit="Datasets",
                           total=1)

    # So we can have an infinite amount of folders or files to go through
    for path in input_file:
        path = Path(path)
        if path.is_dir():
            files = [
                x for x in path.iterdir()
                if x.suffix == ".csv" or x.suffix == ".xlsx"
            ]
            pbar.total = len(files)
            pbar.refresh()
        else:
            pbar.total = 1
            pbar.refresh()
            files = [path]

        for data_file in files:
            status.update('Processing file')
            logging.info("Processing file %s", data_file.stem)
            main(input_file=data_file,
                 output_folder=output_folder,
                 uniform_y_axis=uniform,
                 output_excel=output_excel,
                 correct=offset,
                 iterations=iterations,
                 remove=remove,
                 mag_y_scale=mag_y_scale,
                 diff_y_scale=diff_y_scale)
            bars.close_progress_bars()
            pbar.update()
        inputted_pbar.update()

    pbar.close()
    inputted_pbar.close()
    bars.close_progress_bars()
    logging.info("Program finished, exiting.")


def main(input_file: PathLike,
         output_folder: PathLike = None,
         uniform_y_axis: bool = False,
         output_excel: bool = False,
         correct: bool = False,
         iterations: int = 1,
         remove: str = None,
         mag_y_scale: float = None,
         diff_y_scale: float = None):

    config.filename = input_file
    status = config.pbar_status

    # Extraction and cleanup
    df = io.extract(input_file)
    df = sanitize.remove_incomplete_sets(df)
    df = sanitize.remove_specified_stars(df, remove)

    # Processing
    days = data.group_by_year_month_day(df)

    # Find obviously varying stars
    # perform differential photometry on them
    # Drop=True to prevent index error with Pandas
    # Group by year/month/day to prevent later months from being
    # before earlier months, with an earlier day.
    # e.g. 1/7/2021 being before 22/6/2021
    # TODO make functions for this
    star_detection_method = app_config["star_detection"]["method"]
    status.update(desc="Differential Photometry per day")
    intra_pbar = bars.get_progress_bar(
        name="intra_diff",
        total=len(days),
        desc="  Calculating and finding variable intra-day stars",
        unit="Days",
        color="blue",
        leave=False)
    logging.info("Detecting intra-day variable stars...")
    df = days.apply(
        phot.iterate_differential_photometry,
        method=star_detection_method,
        pbar_method=intra_pbar.update,
        iterations=iterations,
        **app_config[star_detection_method],
        varying_flag="intra_varying",
        detection_data="average_diff_mags",
        detection_error="average_uncertainties").reset_index(drop=True)
    status.update(desc="Differential Photometry per star")
    # TODO don't make the corrected df twice
    df_corrected = ts.correct_offset(df)
    stars = df_corrected.groupby("id")
    # TODO Throw in callback function for inter_pbars
    inter_pbar = bars.get_progress_bar(
        name="inter_diff",
        total=len(stars),
        desc="  Calculating and finding variable inter-day stars",
        unit="Days",
        color="blue",
        leave=False)
    # Detecting if stars are varying across entire dataset
    logging.info("Detecting inter-day variable stars...")

    df[star_detection_method] = stars["average_diff_mags"].transform(
        phot.test_stationarity,
        method=star_detection_method,
        clip=app_config[star_detection_method]["clip"]).reset_index(drop=True)
    inter_pbar.update(len(stars))
    p_value = app_config[star_detection_method]["p_value"]
    null = app_config[star_detection_method]["null"]
    if null == "accept":
        df["inter_varying"] = df[star_detection_method] >= p_value
    else:
        df["inter_varying"] = df[star_detection_method] <= p_value
    # Set all sets of varying stars, so that we can properly graph them
    df = data.flag_intra_variable(df)
    df_corrected = ts.correct_offset(df)
    inter_varying_count = df[df["inter_varying"] == True]["id"].nunique()
    intra_varying_count = df[df["intra_varying"] == True]["id"].nunique()
    unique_varying_count = df[df["intra_varying"]
                              | df["inter_varying"]]["id"].nunique()
    # Correct for any offset found in the data
    logging.info("Total consistently varying stars: %s", inter_varying_count)
    logging.info("Total briefly varying stars: %s", intra_varying_count)
    logging.info("Total variable stars: %s", unique_varying_count)
    logging.info("Starting graphing...")

    if correct == True:
        plot.plot_and_save_all(df=df_corrected,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               corrected=True,
                               output_folder=output_folder,
                               mag_y_scale=mag_y_scale,
                               diff_y_scale=diff_y_scale)
    else:
        plot.plot_and_save_all(df=df,
                               uniform_y_axis=uniform_y_axis,
                               split=True,
                               corrected=True,
                               output_folder=output_folder,
                               mag_y_scale=mag_y_scale,
                               diff_y_scale=diff_y_scale)

    logging.info("Finished graphing")

    if output_excel == True:
        logging.info("Outputting processed dataset as excel...")
        if correct == True:
            io.save_to_excel(df=df_corrected,
                             filename=file.stem,
                             sort_on=["time", "id"],
                             corrected=correct,
                             output_folder=output_folder)
        else:
            io.save_to_excel(df=df,
                             filename=file.stem,
                             sort_on=["time", "id"],
                             corrected=correct,
                             output_folder=output_folder)
        logging.info("Finished excel output")
