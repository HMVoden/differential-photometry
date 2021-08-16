from shutterbug.config.factory import ConfigFactory
from shutterbug.photometry.detect.distance import DistanceDetector
from shutterbug.photometry.detect.expand import ExpandingConditionalDetector
from shutterbug.photometry.detect.magnitude import MagnitudeDetector
import shutterbug.photometry.photometry as photometry
import shutterbug.ux.progress_bars as bars

from benchmarks.benchconf import Data
from shutterbug.photometry.timeseries import StationarityTestFactory


class PhotometrySuite:
    def setup_cache(self):
        data = Data().clean_arranged
        fac = ConfigFactory()
        phot_config = fac.build("photometry")
        stationarity_settings = phot_config.stationarity
        test_method = stationarity_settings["test_method"]
        test_method_settings = phot_config.test[test_method]
        test_fac = StationarityTestFactory()
        intra_variation_test = test_fac.create_test(
            **stationarity_settings,
            test_dimension="time",
            correct_offset=False,
            varying_flag="intra_varying",
            **test_method_settings,
        )
        distance_detector = DistanceDetector(data, **phot_config.distance)
        magnitude_detector = MagnitudeDetector(data, **phot_config.magnitude)
        expanding_detector = ExpandingConditionalDetector(
            magnitude_detector=magnitude_detector,
            distance_detector=distance_detector,
            **phot_config.expanding,
        )
        intraday = photometry.IntradayDifferential(
            iterations=2,
            expanding_detector=expanding_detector,
            stationarity_tester=intra_variation_test,
        )
        return (intraday, data)

    def setup(self, test_intruments):
        bars.init()

    def time_intra_phot_whole(self, test_instruments):
        intraday, data = test_instruments
        intraday.differential_photometry(data)

    def mem_intra_phot_whole(self, test_instruments):
        intraday, data = test_instruments
        intraday.differential_photometry(data)

    def peakmem_intra_phot_whole(self, test_instruments):
        intraday, data = test_instruments
        intraday.differential_photometry(data)
