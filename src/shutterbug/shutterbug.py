import logging.config
from pathlib import Path

import xarray as xr

import shutterbug.config.config as config
import shutterbug.input.input as input
import shutterbug.logging.log as log
import shutterbug.output.output as output
import shutterbug.photometry.photometry as photometry
import shutterbug.ux.progress_bars as bars


def initialize(**cli_settings):
    # Setup logging for verbose output

    bars.init()
    config.ConfigDirector(**cli_settings)


def teardown():
    bars.close_all()
    ConfigDirector().clear_runtime()


def process(input_file: Path):
    config = config.ConfigDirector()
    runtime_config = config.get("runtime")
    runtime_config.add("runtime", input_file)
    input_config = config.get("input")
    app_config = config.get("application")
    plot_config = config.get("plotting")
    cli_config = config.get("cli")


    # WANT
    # TODO Re-organize by program section (input, sanitization, etc)
    # TODO write documentation
    # TODO write function docstrings
    # TODO improve progess bar code
    # TODO add machine learning for star detection
    # TODO write tests for all functions
    # TODO write benchmark code to test memory/CPU use
    # TODO modify diff phot code for xarray
    # TODO refactor plotting for xarray
    # Extraction, cleanup and processing
    # io.extract returns a dataframe which we
    # then move around in a pipe
    (
        io.extract(input_file)
        .pipe(sanitize.drop_and_clean_names, required_data=input_config.get("required"))
        .pipe(sanitize.add_time_information, time_name=input_config.get("time_col_name")
        .pipe(
            sanitize.clean_data,
            coord_names=input_config.get("coords"),
        )
        .pipe(sanitize.drop_duplicate_time)
        .pipe(sanitize.remove_incomplete_stars, stars_to_remove=cli_config.get("remove"))
        .pipe(sanitize.arrange_star_time)
        .pipe(
            photometry.intra_day_iter,
            varying_flag=app_config["varying_flag"],
            app_config=app_config,
            method=app_config["detection_method"],
            iterations=cli_config.get("iterations"),
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
