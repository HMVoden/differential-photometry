import logging
import logging.config

import pandas as pd

import shutterbug.config.config as config
# import shutterbug.data.convert as convert
# import shutterbug.data.load as load
import shutterbug.file_loader as loader
import shutterbug.logging.log as log
import shutterbug.output.figure as plot_util
import shutterbug.output.graph as plot
import shutterbug.output.spreadsheet as spreadsheet
import shutterbug.photometry.photometry as photometry
import shutterbug.sanitizer as sanitize
import shutterbug.ux.progress_bars as bars
from shutterbug.config.data import (CLIConfig, DataConfig, LoggingConfig,
                                    OutputConfig, PhotometryConfig)
from shutterbug.photometry.detect.distance import DistanceDetector
from shutterbug.photometry.detect.expand import ExpandingConditionalDetector
from shutterbug.photometry.detect.magnitude import MagnitudeDetector
from shutterbug.photometry.reducer.reduce_area import dataset_reduce_area
from shutterbug.photometry.timeseries import StationarityTestFactory


def application(input_data, **cli_settings):
    con_dir = config.ConfigDirector(**cli_settings)
    log_config: LoggingConfig = con_dir.get("logging")
    log.initialize_logging(**log_config.dict())
    bars.init()
    data_config: DataConfig = con_dir.get("data")
    phot_config: PhotometryConfig = con_dir.get("photometry")
    cli_config: CLIConfig = con_dir.get("cli")
    out_config: OutputConfig = con_dir.get("output")
    # Extraction, cleanup and processing
    # io.extract returns a dataframe which we
    # then move around in a pipe
    # manager = bars.build(
    #     "files",
    #     "Files processed",
    #     "file",
    #     loader.get_readable_file_count(input_data),
    #     True,
    #     0,
    # )
    readable_files = loader.iload(input_data)
    # with manager as pbar:
    for filename, frame in readable_files:
        logging.info("Starting data loading and sanitization")
        ds = frame.pipe(
            sanitize.sanitize,
            primary_variables=["name", "jd"],
            numeric_variables=["mag", "error", "jd"],
            keep_variables=["name", "mag", "error", "x", "y", "jd"],
        )
        ds["jd"] = pd.to_datetime(ds["jd"], origin="julian", utc=True, unit="D")
        logging.info("Finished sanitizing")
        # ds = (  # Start of load/clean section
        #     frame.pipe(
        #         sanitize.drop_and_clean_names, required_data=data_config.required
        #     )
        #     .pipe(
        #         sanitize.clean_data,
        #         coord_names=data_config.coords,
        #     )
        #     .pipe(convert.add_time_dimension, time_name=data_config.time_col_name)
        #     .pipe(sanitize.drop_duplicate_time)
        #     .pipe(
        #         sanitize.remove_incomplete_stars, stars_to_remove=cli_config.remove
        #     )
        #     .pipe(sanitize.remove_incomplete_time)
        #     .pipe(convert.arrange_star_time)
        # )
        # end of load/clean section
        # generate classes for use
        logging.info("Setting up photometry")
        # bars.status.update(stage="Differential Photometry")
        ds = dataset_reduce_area(ds, reduce_by=(100, 100), image_shape=(4096, 4096))
        stationarity_settings = phot_config.stationarity
        test_method = stationarity_settings["test_method"]
        test_method_settings = phot_config.test[test_method]

        test_fac = StationarityTestFactory()
        logging.debug("Setting up intra variation test")
        intra_variation_test = test_fac.create_test(
            **stationarity_settings,
            test_dimension="time",
            correct_offset=False,
            varying_flag="intra_varying",
            **test_method_settings,
        )
        logging.debug("Setting up inter variation test")
        inter_variation_test = test_fac.create_test(
            **stationarity_settings,
            test_dimension=None,
            correct_offset=cli_config.correct_offset,
            varying_flag="inter_varying",
            **test_method_settings,
        )
        logging.debug("Setting up distance detector")
        distance_detector = DistanceDetector(ds, **phot_config.distance)
        logging.debug("Setting up magnitude detector")
        magnitude_detector = MagnitudeDetector(ds, **phot_config.magnitude)
        logging.debug("Setting up expanding detector system")
        expanding_detector = ExpandingConditionalDetector(
            magnitude_detector=magnitude_detector,
            distance_detector=distance_detector,
            **phot_config.expanding,
        )
        logging.info("Starting photometry and intraday variable star detection")
        intraday = photometry.IntradayDifferential(
            iterations=cli_config.iterations,
            expanding_detector=expanding_detector,
            stationarity_tester=intra_variation_test,
        )
        logging.debug("Finished setup, conducting photometry")
        # photometry and output
        ds = ds.pipe(intraday.differential_photometry)
        bars.status.update(stage="Variation detection")
        logging.info("Beginning variation detection")
        ds = (
            ds.pipe(inter_variation_test.test_dataset)
            # .pipe(log_variable)
            .pipe(
                plot_util.max_variation,
                uniform_y_axis=cli_config.uniform,
                mag_y_scale=cli_config.mag_y_scale,
                diff_y_scale=cli_config.diff_y_scale,
            )
        )
        logging.info("Finished detection")
        ds["varying"] = ds["inter_varying"] | ds["intra_varying"]
        bars.status.update(stage="Output")
        logging.info("Beginning output")
        ds = ds.pipe(
            spreadsheet.save_to_csv,
            filename=filename,
            output_flag=cli_config.output_spreadsheet,
            offset=cli_config.correct_offset,
            output_folder=cli_config.output_folder,
            output_config=out_config.folder,
        ).pipe(
            plot.plot_and_save_all,
            plot_config=out_config.plot,
            uniform_y_axis=cli_config.uniform,
            offset=cli_config.correct_offset,
            output_config=out_config.folder,
            filename=filename,
            dataset=frame,
        )
        bars.status.update(stage="Finishing file")

        # pbar.update()
        # end for loop
    logging.info("Application finished, exiting")


# def log_variable(ds: xr.Dataset):
#     # Extra logging
#     inter_varying_count = ds["inter_varying"].sum(...).data
#     intra_varying_count = (ds["intra_varying"] & ~ds["inter_varying"]).sum(...).data
#     total_varying_count = (ds["intra_varying"] | ds["inter_varying"]).sum(...).data
#     # Correct for any offset found in the data
#     logging.info("Total consistently varying stars: %s", inter_varying_count)
#     logging.info("Total briefly varying stars: %s", intra_varying_count)
#     logging.info("Total combined variable stars: %s", total_varying_count)
#     return ds
