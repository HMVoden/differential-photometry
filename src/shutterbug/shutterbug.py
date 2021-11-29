import gc
import logging.config
from pathlib import Path

import xarray as xr

import shutterbug.config.manager as config
import shutterbug.data.input_output as io
import shutterbug.data.sanitize as sanitize
import shutterbug.photometry.differential as photometry
import shutterbug.plotting.plot as plot
import shutterbug.plotting.utilities as plot_util
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

    # NEED
    # TODO write function that finds nearby stars
    # TODO write function that finds stars less than 0.5 mag dimmer
    # TODO write function that scales restrictions to get minimum # of stars
    # TODO write blitting functions for graphing
    # WANT
    # TODO Re-organize by program section (input, sanitization, etc)
    # TODO write documentation
    # TODO write function docstrings
    # TODO improve progess bar code
<<<<<<< HEAD:src/shutterbug/shutterbug.py
    # TODO fix progress bars not finishing
=======
>>>>>>> 14fa39af25ec1544244fc9637b3cec17f30b372f:shutterbug/shutterbug.py
    # TODO add machine learning for star detection
    # TODO write tests for all functions
    # TODO write benchmark code to test memory/CPU use
    # Extraction, cleanup and processing
    # io.extract returns a dataframe which we
    # then move around in a pipe
    (
        io.extract(input_file)
        .pipe(sanitize.drop_and_clean_names, required_data=input_config["required"])
        .pipe(sanitize.add_time_information, time_name=input_config["time"])
        .pipe(sanitize.clean_data, coord_names=input_config["coords"],)
        .pipe(sanitize.drop_duplicates)
        .pipe(sanitize.remove_incomplete_stars, stars_to_remove=config.get("remove"))
        .pipe(sanitize.arrange_star_time)
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
