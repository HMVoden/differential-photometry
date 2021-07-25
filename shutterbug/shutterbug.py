import gc
import logging.config

from pathlib import Path
import config.manager as config
import xarray as xr

import shutterbug.data.input_output as io
import shutterbug.data.sanitize as sanitize
import shutterbug.photometry.differential as photometry
import shutterbug.plot.plot as plot
import shutterbug.plot.utilities as plot_util
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
    plot_config = config.get("plotting")

    # Extraction, cleanup and processing
    # io.extract returns a dataframe which we
    # then move around in a pipe
    # TODO write function that finds nearby stars
    # TODO write function that finds stars less than 0.5 mag dimmer
    # TODO write blitting functions for graphing
    (
        io.extract(input_file)
        .pipe(sanitize.drop_and_clean_names, input_config["required"])
        .pipe(
            sanitize.clean_data,
            coord_names=input_config["coords"],
            time_name=input_config["time"],
        )
        .pipe(sanitize.remove_incomplete_sets, config.get("remove"))
        .pipe(sanitize.arrange_data)
        .pipe(
            photometry.intra_day_iter,
            varying_flag=app_config["varying_flag"],
            app_config=app_config,
            method=app_config["detection_method"],
            iterations=config.get("iterations"),
        )
        .pipe(ts.correct_offset)
        .pipe(
            photometry.inter_day,
            app_config=app_config,
            method=app_config["detection_method"],
        )
        .pipe(log_variable)
        .pipe(
            plot_util.max_variation,
            uniform_y_axis=config.get("uniform"),
            mag_y_scale=config.get("mag_y_scale"),
            diff_y_scale=config.get("diff_y_scale"),
        )
        .pipe(
            plot.plot_and_save_all,
            plot_config=plot_config,
            uniform_y_axis=config.get("uniform"),
            offset=config.get("offset"),
        )
        .pipe(
            io.save_to_csv,
            filename=input_file.stem,
            offset=config.get("offset"),
            output_folder=config.get("output_folder"),
            output_flag=config.get("output_excel"),
        )
    )


def log_variable(ds: xr.Dataset):
    # Extra logging
    inter_varying_count = ds["inter_varying"].sum(...).data
    intra_varying_count = (ds["intra_varying"] & ~ds["inter_varying"]).sum(...).data
    total_varying_count = (ds["intra_varying"] | ds["inter_varying"]).sum(...).data
    # Correct for any offset found in the data
    logging.info("Total consistently varying stars: %s", inter_varying_count)
    logging.info("Total briefly varying stars: %s", intra_varying_count)
    logging.info("Total combined variable stars: %s", total_varying_count)
    return ds
