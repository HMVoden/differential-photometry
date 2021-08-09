import logging
import logging.config
from pathlib import Path

import xarray as xr

import shutterbug.config.config as config
import shutterbug.data.convert as convert
import shutterbug.data.load as load
import shutterbug.data.sanitize as sanitize
import shutterbug.logging.log as log
import shutterbug.output.graph as graph
import shutterbug.output.spreadsheet as ss
import shutterbug.photometry.photometry as photometry
import shutterbug.ux.progress_bars as bars
from shutterbug.config.data import (CLIConfig, DataConfig, LoggingConfig,
                                    OutputConfig, PhotometryConfig,
                                    RuntimeConfig)


def teardown():
    bars.close_all()
    config.ConfigDirector().clear_runtime()


def application(**cli_settings):
    con_dir = config.ConfigDirector(**cli_settings)
    bars.init()
    data_config: DataConfig = con_dir.get("data")
    log_config: LoggingConfig = con_dir.get("logging")
    phot_config: PhotometryConfig = con_dir.get("photometry")
    cli_config: CLIConfig = con_dir.get("cli")
    out_config: OutputConfig = con_dir.get("output")

    # WANT
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
    for file in cli_config.input_data:
        if file.suffix in data_config.reader["types"].keys():

            (
                load.from_file(file, data_config.reader)
                .pipe(sanitize.drop_and_clean_names, required_data=data_config.required)
                .pipe(
                    sanitize.clean_data,
                    coord_names=data_config.coords,
                )
                .pipe(sanitize.drop_duplicate_time)
                .pipe(
                    sanitize.remove_incomplete_stars, stars_to_remove=cli_config.remove
                )
                .pipe(convert.add_time, time_name=data_config.time_col_name)
                .pipe(convert.arrange_star_time)
                .pipe(
                    photometry.intra_day_iter,
                    varying_flag=app_config.varying_flag,
                    app_config=app_config,
                    method=app_config.detection_method,
                    iterations=cli_config.iterations,
                )
                .pipe(ts.correct_offset)
                .pipe(
                    photometry.inter_day,
                    app_config=app_config,
                    method=app_config.detection_method,
                )
                .pipe(log_variable)
                .pipe(
                    plot_util.max_variation,
                    uniform_y_axis=cli_config.uniform,
                    mag_y_scale=cli_config.mag_y_scale,
                    diff_y_scale=cli_config.diff_y_scale,
                )
                .pipe(
                    plot.plot_and_save_all,
                    plot_config=plot_config,
                    uniform_y_axis=cli_config.uniform,
                    offset=cli_config.correct_offset,
                )
                .pipe(
                    io.save_to_csv,
                    filename=input_file.stem,
                    offset=cli_config.correct_offset,
                    output_folder=cli_config.output_folder,
                    output_flag=cli_config.output_spreadsheet,
                )
            )
            teardown()
        logging.info("Application finished, exiting")


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
