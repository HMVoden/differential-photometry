# %%
import importlib
import logging.config
import time
import warnings
from pathlib import Path, PurePath

import pandas as pd
import toml
# from feets import ExtractorWarning

import differential_photometry.analysis as analysis
import differential_photometry.data as data
import differential_photometry.differential_photometry as diff
import differential_photometry.models as model
import differential_photometry.plotting as plot
import differential_photometry.stats as stat
import differential_photometry.utilities as util
# import differential_photometry.config as config

importlib.reload(util)
importlib.reload(analysis)
importlib.reload(data)
importlib.reload(diff)
importlib.reload(plot)
importlib.reload(model)
importlib.reload(stat)

# CONSTANTS ============================================================================
# FILENAME = 'data.csv'
# FILENAME = "M3_raw01_Photometry25-47-59.csv"
# FILENAME = "M3_2nights_rawPhotometry.csv"
# FILENAME = 'M3_night_1.xlsx'
# FILENAME = 'M3_night_2.xlsx'
FILENAME = "M92_rawPhotometry_v01_total.csv"
# FILENAME = 'M92_rawPhotometry_v02_total.csv'

# Need this to prevent it from spamming
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
# warnings.filterwarnings("ignore", category=ExtractorWarning)
warnings.filterwarnings("ignore", category=UserWarning)

app_config = toml.load("config/application.toml")
plot_config = toml.load("config/plotting.toml")

if __name__ == "__main__":

    if app_config["time_execution"] == True:
        start_time = time.time()
    if app_config['logging']['enabled'] == True:
        log_config = toml.load("config/logging.toml")
        logging.config.dictConfig(log_config)
        logging.debug("Logging configured")

    data_directory = Path(app_config["input"]["directory"])
    file = data_directory.joinpath(FILENAME)
    # this is very bad form, but needed for parallel
    # because I don't know how to work with that properly
    with open("config/working.toml", "w") as f:
        toml.dump({"current_file": file}, f)

    df = data.extract(file)

    df = data.remove_incomplete_sets(df)

    days = df.groupby("d_m_y")

    # Find obviously varying stars
    # perform differential photometry on them
    # Drop=True to prevent index error with Pandas
    df = days.apply(
        util.find_varying_diff_calc,
        method="adf_gls",
        threshold=0.05,  # p-value
        null="accept",  # reject or accept null
        clip=False).reset_index(drop=True)

    # Set all sets of varying stars, so that we can properly graph them
    df = util.flag_variable(df)
    # Correct for any offset found in the data
    df_corrected = util.correct_offset(df)

    # TODO make function and use natsort on this
    # df_corrected.sort_values(by=["time", "name"], axis="index", inplace=True)
    # df[df["varying"] == True].to_excel((file.stem + "_varying.xlsx"))
    # df[df["varying"] == False].to_excel((file.stem + "_non_varying.xlsx"))
    # df_corrected[df_corrected["varying"] == True].to_excel(
    #     (file.stem + "_varying_offset.xlsx"))
    # df_corrected[df_corrected["varying"] == False].to_excel(
    #     (file.stem + "_non_varying_offset.xlsx"))

    # Timing for my edification
    if app_config["time_execution"] == True:
        pre_graph_time = time.time()
        non_graph_runtime = pre_graph_time - start_time
        logging.info("Application ran in %1.2f seconds", non_graph_runtime)

    logging.info("Starting graphing")

    # plot.plot_and_save_all(df=df, uniform_y_axis=True, split=True)
    # plot.plot_and_save_all(df=df_corrected, uniform_y_axis=True, split=True)

    logging.info("Finished graphing")
    if app_config["time_execution"] == True:
        graph_runtime = time.time() - pre_graph_time
        total_time = time.time() - start_time
        logging.info("Graphing ran in %1.2f seconds", graph_runtime)
        logging.info("Total application runtime is: %1.2f seconds", total_time)
