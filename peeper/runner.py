import gc
import logging.config
from os import PathLike

import config.manager as config
import pandas as pd

import peeper.data.input_output as io
import peeper.data.sanitize as sanitize
import peeper.data.utilities as data
import peeper.photometry.photometry as photometry
import peeper.plot.plot as plot
import peeper.progress_bars as bars
import peeper.timeseries.timeseries as ts


def initialize(**settings):
    config.load_file_configuration()
    # Setup logging for verbose output
    if config.get("application")["logging"]["enabled"] == True:
        log_config = config.get("logging")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    logging.info("Application initialized successfully")

    bars.init_progress_bars()
    config.init_configuration(**settings)


def teardown():
    bars.close_progress_bars()


def run(input_file: PathLike):

    config.update("filename", input_file)
    status = bars.status

    # Extraction, cleanup and processing
    df = (
        io.extract(input_file)
        .pipe(sanitize.remove_incomplete_sets)
        .pipe(photometry.intra_day_iter)
        .pipe(ts.correct_offset)
        .pipe(photometry.inter_day)
        .pipe(data.flag_variable)
        .pipe(log_variable)
    )
    gc.collect()

    plot.plot_and_save_all(
        df=df.drop(columns=["mag_offset", "diff_mag_offset", "adf_gls", "x", "y"])
    )

    logging.info("Finished graphing")
    output_excel = config.get("output_excel")
    if output_excel == True:
        status.update(demo="Writing excel")
        logging.info("Outputting processed dataset as excel...")
        output_folder = config.get("output_folder")
        correct = config.get("offset")
        io.save_to_excel(
            df=df,
            filename=input_file.stem,
            sort_on=["time", "id"],
            corrected=correct,
            output_folder=output_folder,
        )
        logging.info("Finished excel output")
    status.update(demo="Wrapping up")


def log_variable(df: pd.DataFrame):
    # Set all sets of varying stars, so that we can properly graph them
    # Extra logging
    inter_varying_count = df[df["inter_varying"] == True]["id"].nunique()
    intra_varying_count = df[df["intra_varying"] == True]["id"].nunique()
    unique_varying_count = df[df["intra_varying"] | df["inter_varying"]]["id"].nunique()
    # Correct for any offset found in the data
    logging.info("Total consistently varying stars: %s", inter_varying_count)
    logging.info("Total briefly varying stars: %s", intra_varying_count)
    logging.info("Total variable stars: %s", unique_varying_count)
    logging.info("Starting graphing...")
    return df
