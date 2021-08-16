import benchmarks.benchconf as bf
from shutterbug.config.factory import ConfigFactory
import shutterbug.photometry.detect.magnitude as magnitude


class MagnitudeSuite:
    def setup_cache(self):
        data = bf.Data().clean_arranged
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        magnitude_detector = magnitude.MagnitudeDetector(data, **phot_config.magnitude)
        return magnitude_detector, data


class TimeSuite(MagnitudeSuite):
    def time_magnitude_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        magnitude.MagnitudeDetector(data, **phot_config.magnitude)

    def time_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def time_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def time_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()

    def time_calc_tolerance_range(self, test_instruments):
        detector, _ = test_instruments
        detector.calculate_tolerance_range()


class ParamSuite(MagnitudeSuite):
    params = [[1, 2, 5, 10, 20]]
    param_names = ["iterations"]

    def time_magnitude(
        self,
        test_instruments,
        iterations,
    ):
        detector, data = test_instruments
        stars = data.star.values[
            : iterations + 1
        ]  # +1 because slice is exclusive on end
        for star in stars:
            detector.detect(star)

    def mem_magnitude(
        self,
        test_instruments,
        iterations,
    ):
        detector, data = test_instruments
        stars = data.star.values[
            : iterations + 1
        ]  # +1 because slice is exclusive on end
        for star in stars:
            detector.detect(star)

    def peakmem_magnitude(
        self,
        test_instruments,
        iterations,
    ):
        detector, data = test_instruments
        stars = data.star.values[
            : iterations + 1
        ]  # +1 because slice is exclusive on end
        for star in stars:
            detector.detect(star)


class MemSuite(MagnitudeSuite):
    def mem_magnitude_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        magnitude.MagnitudeDetector(data, **phot_config.magnitude)

    def mem_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def mem_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def mem_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()

    def mem_calc_tolerance_range(self, test_instruments):
        detector, _ = test_instruments
        detector.calculate_tolerance_range()


class PeakMemSuite(MagnitudeSuite):
    def peakmem_magnitude_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        magnitude.MagnitudeDetector(data, **phot_config.magnitude)

    def peakmem_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def peakmem_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def peakmem_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()

    def peakmem_calc_tolerance_range(self, test_instruments):
        detector, _ = test_instruments
        detector.calculate_tolerance_range()
