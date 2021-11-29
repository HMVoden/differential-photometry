import benchmarks.benchconf as bf
from shutterbug.config.factory import ConfigFactory
import shutterbug.photometry.detect.distance as distance


class DistanceSuite:
    def setup_cache(self):
        data = bf.Data().clean_arranged
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        distance_detector = distance.DistanceDetector(data, **phot_config.distance)
        return distance_detector, data


class TimeSuite(DistanceSuite):
    def time_distance_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        distance.DistanceDetector(data, **phot_config.distance)

    def time_distance_build_tree(self, test_instruments):
        detector, data = test_instruments
        detector._build_kd_tree(data["x"].values, data["y"].values)

    def time_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def time_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def time_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()


class ParamSuite(DistanceSuite):
    params = [[1, 2, 5, 10, 20]]
    param_names = ["iterations"]

    def time_distance(
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

    def mem_distance(
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

    def peakmem_distance(
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


class MemSuite(DistanceSuite):
    def mem_distance_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        distance.DistanceDetector(data, **phot_config.distance)

    def mem_distance_build_tree(self, test_instruments):
        detector, data = test_instruments
        detector._build_kd_tree(data["x"].values, data["y"].values)

    def mem_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def mem_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def mem_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()


class PeakMemSuite(DistanceSuite):
    def peakmem_distance_setup(self, test_intruments):
        _, data = test_intruments
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        distance.DistanceDetector(data, **phot_config.distance)

    def peakmem_distance_build_tree(self, test_instruments):
        detector, data = test_instruments
        detector._build_kd_tree(data["x"].values, data["y"].values)

    def peakmem_expand(self, test_instruments):
        detector, _ = test_instruments
        detector.expand()

    def peakmem_contract(self, test_instruments):
        detector, _ = test_instruments
        detector.contract()

    def peakmem_reset_increment(self, test_instruments):
        detector, _ = test_instruments
        detector.reset_increment()
