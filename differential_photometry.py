# %%
import importlib
import logging.config
import time
import warnings
from pathlib import Path, PurePath

import pandas as pd
import toml
from feets import ExtractorWarning

import differential_photometry.rao_analysis as analysis
import differential_photometry.rao_data as data
import differential_photometry.rao_differential_photometry as diff
import differential_photometry.rao_math as m
import differential_photometry.rao_models as model
import differential_photometry.rao_plotting as plot
import differential_photometry.rao_stats as stat
import differential_photometry.rao_utilities as util

importlib.reload(m)
importlib.reload(util)
importlib.reload(analysis)
importlib.reload(data)
importlib.reload(diff)
importlib.reload(plot)
importlib.reload(model)
importlib.reload(stat)

# CONSTANTS ============================================================================
# FILENAME = 'data/data.csv'
# FILENAME = "data/M3_raw01_Photometry25-47-59.csv"
FILENAME = "data/M3_2nights_rawPhotometry.csv"
# FILENAME = 'data/M3_night_1.xlsx'
# FILENAME = 'data/M3_night_2.xlsx'
# FILENAME = "data/M92_rawPhotometry_v01_total.csv"
# FILENAME = 'data/M92_rawPhotometry_v02_total.csv'

# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# CALCULATION ============================================================================

if __name__ == "__main__":
    config = toml.load("config/application.toml")
    if config["time_execution"] is True:
        start_time = time.time()
    if config['logging']['enabled'] is True:
        log_config = toml.load("config/logging.toml")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")

    file = PurePath(FILENAME)
    dataset = file.stem.split("_")[0]

    df = data.extract(FILENAME)

    df = data.remove_incomplete_sets(df)

    days = df.groupby("d_m_y")

    processed_frames = []
    # Step 1, find obviously varying stars
    # perform differential photometry on them
    for name, frame in days:
        logging.info("Processing dataframe for day %s", name)
        non_varying, varying = analysis.find_varying_stars(frame, threshold=5)

        frame = diff.calculate_differential_photometry(df=non_varying,
                                                       varying=varying)

        logging.info(
            "Total varying stars in day %s: %s",
            name,
            varying["name"].nunique(),
        )

        processed_frames.append(frame)

    df = pd.concat(processed_frames, join="outer")
    df = util.flag_variable(df)
    # Correct for any offset found in the data
    df_corrected = util.correct_offset(df)

    # Set all sets of varying stars, so that we can properly graph them
    varying = df_corrected[df_corrected["varying"] == True]
    non_varying = df_corrected[df_corrected["varying"] == False]

    if config["time_execution"] is True:
        pre_graph_time = time.time()
        non_graph_runtime = pre_graph_time - start_time
        logging.info("Application ran in %1.2f seconds", non_graph_runtime)
    logging.info("Starting graphing")
    # # # Plotting
    # # # plot.plot_and_save_all(
    # # #     detrended_non_varying, ("detrended/detrended_non_varying_" + file.stem))
    # # # plot.plot_and_save_all(
    # # #     detrended_varying, ("detrended/detrended_varying_" + file.stem))
    # # # plot.plot_and_save_all(varying, ("varying/varying_" + file.stem))
    # # # plot.plot_and_save_all(
    # # #     non_varying, ("non_varying/non_varying_" + file.stem))
    output = config['output']['base']
    output['dataset'] = dataset
    output['filename'] = file.stem
    output.update(config['output']['corrected'])
    plot.plot_and_save_all(df=varying,
                           uniform_y_axis=False,
                           **output,
                           **config['output']['varying'])
    plot.plot_and_save_all(df=non_varying,
                           uniform_y_axis=False,
                           **output,
                           **config['output']['non_varying'])
    logging.info("Finished graphing")
    if config["time_execution"] is True:
        graph_runtime = time.time() - pre_graph_time
        total_time = time.time() - start_time
        logging.info("Graphing ran in %1.2f seconds", graph_runtime)
        logging.info("Total application runtime is: %1.2f seconds", total_time)
