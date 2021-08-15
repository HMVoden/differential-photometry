import benchmarks.benchconf as bf
import shutterbug.data.sanitize as sanitize
import shutterbug.data.convert as convert


class SanitizeSuite:
    def setup_cache(self):
        self.raw = bf.Data().raw
        self.raw_with_time = convert.add_time_dimension(self.raw, "jd")

    def time_check_and_coerce(self):
        raw = self.raw
        raw.map(sanitize.check_and_coerce_dataarray)

    def time_clean_names(self):
        raw = self.raw
        raw.pipe(sanitize.clean_names, list(raw.variables.keys()))

    def time_drop_duplicate_time(self):
        raw = self.raw_with_time
        raw.pipe(sanitize.drop_duplicate_time)

    def time_clean_data(self):
        raw = self.raw
        raw.pipe(sanitize.clean_data, ["obj", "name", "mag", "error", "x", "y", "jd"])

    def time_drop_and_clean_names(self):
        raw = self.raw
        raw.pipe(sanitize.drop_and_clean_names, list(raw.variables.keys()))
