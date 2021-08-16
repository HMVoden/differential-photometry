# Write the benchmarking functions here.
# See "Writing benchmarks" in the asv docs for more information.
from importlib.resources import files

import benchmarks.test_data as test_data

import shutterbug.data.sanitize as sanitize
import shutterbug.data.convert as convert
import shutterbug.ux.progress_bars as bars

import xarray as xr
import pandas as pd


class Singleton:
    _instance = None  # Keep instance reference

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance


class Data(Singleton):
    """Loads all the data a single time for use"""

    clean_arranged: xr.Dataset
    clean: xr.Dataset
    raw: xr.Dataset

    def __init__(self):
        bars.init()
        raw = [x for x in files(test_data).iterdir() if x.suffix == ".csv"]
        df = pd.read_csv(raw[0])
        self.raw = df.to_xarray()
        self.clean = self.load_and_clean()
        self.clean_arranged = self.clean.pipe(convert.arrange_star_time)

    def load_and_clean(self):
        dataset = self.raw
        ds = (
            dataset.pipe(
                sanitize.drop_and_clean_names,
                required_data=["obj", "name", "mag", "error", "x", "y", "jd"],
            )
            .pipe(
                sanitize.clean_data,
                coord_names=["star", "x", "y", "jd"],
            )
            .pipe(convert.add_time_dimension, time_name="jd")
            .pipe(sanitize.drop_duplicate_time)
            .pipe(sanitize.remove_incomplete_stars)
            .pipe(sanitize.remove_incomplete_time)
        )

        return ds
