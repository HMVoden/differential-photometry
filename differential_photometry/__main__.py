import logging.config
import warnings
from os import PathLike
from pathlib import Path

import click
import toml
import enlighten

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


@click.command()
@click.argument("input_file",
                type=click.Path(file_okay=True, dir_okay=True, exists=True),
                nargs=-1,
                required=True)
@click.option("-o",
              "--output_folder",
              default=None,
              type=click.Path(file_okay=False, dir_okay=True, exists=False),
              help="Root output directory for excel and graphs")
@click.option(
    "-u",
    "--uniform/--no-uniform",
    default=False,
    help="Flag whether the graphed dataset should share y-axis limits")
@click.option("-e",
              "--output_excel/--no_excel",
              default=False,
              help="Whether to output to excel")
@click.option("-f",
              "--offset/--no_offset",
              default=False,
              help="Whether to correct offset between days in the graphs")
def runner(input_file: Path, output_folder: Path, uniform: bool,
           output_excel: bool, offset: bool):
    with enlighten.get_manager() as manager:
        config.pbar_man = manager  # set up universal progress bar manager

        status = manager.status_bar(
            status_format=u'{fill}Stage: {demo}{fill}{elapsed}',
            color='bold_underline_bright_white_on_lightslategray',
            justify=enlighten.Justify.CENTER,
            demo='Reading data',
            autorefresh=True,
            min_delta=0.5)

        config.pbar_status = status

        # Setup logging for verbose output
        if app_config['logging']['enabled'] == True:
            log_config = toml.load("config/logging.toml")
            logging.config.dictConfig(log_config)
            logging.debug("Logging configured")
        pbar = manager.counter(total=len(input_file),
                               desc="Reading data",
                               unit="Datasets")
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
                    main(data_file, output_folder, uniform, output_excel,
                         offset)
                    pbar.update()
            else:
                logging.info("Processing file %s", path.stem)
                main(path, output_folder, uniform, output_excel, offset)
                pbar.update()
        pbar.close()
        logging.info("Program finished, exiting.")


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

    # Find obviously varying stars
    # perform differential photometry on them
    # Drop=True to prevent index error with Pandas
    days = df.groupby("d_m_y")
    star_detection_method = app_config["star_detection"]["method"]
    df = days.apply(phot.find_varying_diff_calc,
                    method=star_detection_method,
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
