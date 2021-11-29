from benchmarks.benchconf import Data
from shutterbug.data.convert import add_time_dimension, arrange_star_time


class ConvertSuite:
    def setup(self):
        self.clean = Data().clean


class TimeSuite(ConvertSuite):
    def time_arrange_star_time(self):
        self.clean.pipe(arrange_star_time)

    def time_add_time_dimension(self):
        self.clean.pipe(add_time_dimension, "jd")


class MemSuite(ConvertSuite):
    def mem_arrange_star_time(self):
        self.clean.pipe(arrange_star_time)

    def mem_add_time_dimension(self):
        self.clean.pipe(add_time_dimension, "jd")


class PeakMemSuite(ConvertSuite):
    def peakmem_arrange_star_time(self):
        self.clean.pipe(arrange_star_time)

    def peakmem_add_time_dimension(self):
        self.clean.pipe(add_time_dimension, "jd")
