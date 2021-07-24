import gc
import logging.config

from pathlib import Path
import config.manager as config
import xarray as xr

import shutterbug.data.input_output as io
import shutterbug.data.sanitize as sanitize
import shutterbug.data.utilities as data
import shutterbug.photometry.differential as photometry
import shutterbug.plot.plot as plot
import shutterbug.progress_bars as bars
import shutterbug.timeseries.timeseries as ts


def initialize(**settings):
    config.load_file_configuration()
    # Setup logging for verbose output
    if config.get("application")["logging"]["enabled"] == True:
        log_config = config.get("logging")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")
    logging.info("Application initialized successfully")

    bars.init()
    config.init_configuration(**settings)


def teardown():
    bars.close_all()


def process(input_file: Path):

    config.update("filename", input_file)
    input_config = config.get("input")
    app_config = config.get("application")

    # Extraction, cleanup and processing
    # io.extract returns a dataframe which we
    # then move around in a pipe
    # TODO write function that removes duplicates
    # TODO write function that finds nearby stars
    # TODO write function that finds stars less than 0.5 mag dimmer
    # TODO convert to xarray
    # TODO @guvectorize differential photometry modules
    # TODO write blitting functions for graphing
    df = (
        io.extract(input_file)
        .pipe(sanitize.drop_and_clean_names, input_config["required"])
        .pipe(sanitize.remove_incomplete_sets, config.get("remove"))
        .pipe(
            sanitize.clean_data,
            input_config["coords"],
            input_config["time"],
        )
        .pipe(sanitize.arrange_data)
        .pipe(photometry.intra_day_iter)
        .pipe(ts.correct_offset)
        .pipe(photometry.inter_day)
        .pipe(log_variable)
        .pipe(plot.plot_and_save_all)
    )

    logging.info("Finished graphing")
    output_excel = config.get("output_excel")
    if output_excel == True:
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


def log_variable(ds: xr.Dataset):
    # Set all sets of varying stars, so that we can properly graph them
    # Extra logging
    inter_varying_count = (
        (ds["inter_varying"] & ~ds["intra_varying"])
        .groupby("star")
        .all(...)
        .sum(...)
        .data
    )
    intra_varying_count = ds["intra_varying"].groupby("star").any(...).sum(...).data
    total_varying_count = (
        (ds["intra_varying"] | ds["inter_varying"])
        .groupby("star")
        .all(...)
        .sum(...)
        .data
    )
    # Correct for any offset found in the data
    logging.info("Total consistently varying stars: %s", inter_varying_count)
    logging.info("Total briefly varying stars: %s", intra_varying_count)
    logging.info("Total combined variable stars: %s", total_varying_count)
    return ds
