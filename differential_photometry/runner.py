import logging.config
from os import PathLike

import differential_photometry.data.utilities as data
import differential_photometry.plot.plot as plot
import differential_photometry.data.input_output as io
import differential_photometry.photometry.photometry as photometry
import differential_photometry.data.sanitize as sanitize
import differential_photometry.progress_bars as bars

import config.manager as config


def initialize(**settings):
    bars.init_progress_bars()
    config.init_configuration(**settings)
    # Setup logging for verbose output
    if config.get("application")['logging']['enabled'] == True:
        log_config = config.get("logging")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    logging.info("Application initialized successfully")


def teardown():
    bars.close_progress_bars()


def run(input_file: PathLike):

    config.update("filename", input_file)
    status = bars.status
    stars_to_remove = config.get("remove")

    # Extraction and cleanup
    df = io.extract(input_file)
    df = sanitize.remove_incomplete_sets(df)
    df = sanitize.remove_specified_stars(df, stars_to_remove)

    # Processing
    status.update(demo="Calculating photometry and finding variable stars")
    df = photometry.intra_day_iter(df)
    df = photometry.inter_day(df)

    # Set all sets of varying stars, so that we can properly graph them
    df = data.flag_variable(df)
    # Extra logging
    inter_varying_count = df[df["inter_varying"] == True]["id"].nunique()
    intra_varying_count = df[df["intra_varying"] == True]["id"].nunique()
    unique_varying_count = df[df["intra_varying"]
                              | df["inter_varying"]]["id"].nunique()
    # Correct for any offset found in the data
    logging.info("Total consistently varying stars: %s", inter_varying_count)
    logging.info("Total briefly varying stars: %s", intra_varying_count)
    logging.info("Total variable stars: %s", unique_varying_count)
    logging.info("Starting graphing...")

    plot.plot_and_save_all(df=df)

    logging.info("Finished graphing")
    output_excel = config.get("output_excel")
    if output_excel == True:
        status.update(demo="Writing excel")
        logging.info("Outputting processed dataset as excel...")
        output_folder = config.get("output_folder")
        correct = config.get("offset")
        io.save_to_excel(df=df,
                         filename=input_file.stem,
                         sort_on=["time", "id"],
                         corrected=correct,
                         output_folder=output_folder)
        logging.info("Finished excel output")
    status.update(demo="Wrapping up")