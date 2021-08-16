import benchmarks.benchconf as bf
import shutterbug.data.sanitize as sanitize
import shutterbug.data.convert as convert

import xarray as xr


class SanitizeSuite:
    raw: xr.Dataset
    raw_with_time: xr.Dataset

    def _clean_raw(self):
        raw_with_time = self.raw.pipe(
            sanitize.drop_and_clean_names,
            ["obj", "name", "mag", "error", "x", "y", "jd"],
        )
        raw_with_time = raw_with_time.pipe(
            sanitize.clean_data, ["star", "x", "y", "jd"]
        )
        self.raw_with_time = convert.add_time_dimension(raw_with_time, "jd")

    def setup(self):
        self.raw = bf.Data().raw
        self._clean_raw()


class TimeSuite(SanitizeSuite):
    def time_check_and_coerce(self):
        raw = self.raw
        raw.map(sanitize.check_and_coerce_dataarray)

    def time_clean_names(self):
        raw = self.raw
        raw.pipe(sanitize.clean_names)

    def time_drop_duplicate_time(self):
        raw = self.raw_with_time
        raw.pipe(sanitize.drop_duplicate_time)

    def time_clean_data(self):
        raw = self.raw_with_time
        raw.pipe(sanitize.clean_data, ["star", "x", "y", "jd", "time"])

    def time_drop_and_clean_names(self):
        raw = self.raw
        raw.pipe(
            sanitize.drop_and_clean_names,
            ["obj", "name", "mag", "error", "x", "y", "jd"],
        )

    def time_clean_header(self):
        for header in list(self.raw.variables.keys()):
            sanitize.clean_header(header)

    def time_find_nan_stars(self):
        sanitize.find_nan_stars(self.raw_with_time)

    def time_find_wrong_count_time(self):
        sanitize.find_wrong_count_time(self.raw_with_time)

    def time_find_wrong_count_star(self):
        sanitize.find_wrong_count_stars(self.raw_with_time)

    def time_remove_incomplete_time(self):
        sanitize.remove_incomplete_time(self.raw_with_time)

    def time_remove_incomplete_stars(self):
        sanitize.remove_incomplete_stars(self.raw_with_time)

    def time_remove_all_stars(
        self,
    ):
        self.raw_with_time.pipe(sanitize.remove_stars, self.raw_with_time.star.values)

    def time_remove_all_time(
        self,
    ):
        self.raw_with_time.pipe(sanitize.remove_time, self.raw_with_time.time.values)

    def time_remove_some_stars(
        self,
    ):
        self.raw_with_time.pipe(
            sanitize.remove_stars, self.raw_with_time.star.values[:3]
        )

    def time_remove_some_time(
        self,
    ):
        self.raw_with_time.pipe(
            sanitize.remove_time, self.raw_with_time.time.values[:3]
        )


class PeakMemSuite(SanitizeSuite):
    def peakmem_check_and_coerce(self):
        raw = self.raw
        raw.map(sanitize.check_and_coerce_dataarray)

    def peakmem_clean_names(self):
        raw = self.raw
        raw.pipe(sanitize.clean_names)

    def peakmem_drop_duplicate_time(self):
        raw = self.raw_with_time
        raw.pipe(sanitize.drop_duplicate_time)

    def peakmem_clean_data(self):
        raw = self.raw_with_time
        raw.pipe(sanitize.clean_data, ["star", "x", "y", "jd", "time"])

    def peakmem_drop_and_clean_names(self):
        raw = self.raw
        raw.pipe(
            sanitize.drop_and_clean_names,
            ["obj", "name", "mag", "error", "x", "y", "jd"],
        )

    def peakmem_clean_header(self):
        for header in list(self.raw.variables.keys()):
            sanitize.clean_header(header)

    def peakmem_find_nan_stars(self):
        sanitize.find_nan_stars(self.raw_with_time)

    def peakmem_find_wrong_count_time(self):
        sanitize.find_wrong_count_time(self.raw_with_time)

    def peakmem_find_wrong_count_time(self):
        sanitize.find_wrong_count_stars(self.raw_with_time)

    def peakmem_remove_incomplete_time(self):
        sanitize.remove_incomplete_time(self.raw_with_time)

    def peakmem_remove_incomplete_stars(self):
        sanitize.remove_incomplete_stars(self.raw_with_time)
