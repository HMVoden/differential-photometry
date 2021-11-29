from benchmarks.benchconf import Data

import shutterbug.photometry.differential as diff
import numpy as np
import math


class DifferentialSuite:
    def setup(self):
        self.data = Data().clean_arranged
        data_size = self.data.star.size
        if data_size % 2 == 0:  # even
            size = int(data_size / 2)
            false = np.full(self.data["star"].size / 2, False).tolist()
            true = np.full(self.data["star"].size / 2, True).tolist()
            false.extend(true)
            varying_list = false

            self.data.coords["varying"] = (
                "star",
                varying_list,
            )
        if data_size % 2 == 1:  # odd
            size = int(math.floor(data_size / 2))
            false = np.full(size, False).tolist()
            true = np.full(size, True).tolist()
            # add one extra so it fits
            false.append(False)
            false.extend(true)
            varying_list = false
            self.data.coords["varying"] = (
                "star",
                varying_list,
            )

        self.varying = self.data.where(self.data["varying"] == True, drop=True)
        self.non_varying = self.data.where(self.data["varying"] == False, drop=True)


class TimeSuite(DifferentialSuite):
    def time_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.magnitude(non_varying.mag.values, varying.mag.values)

    def time_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.error(non_varying.error.values, varying.error.values)

    def time_calculate_diff_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_magnitude(
            non_varying.mag.values.transpose(), varying.mag.values.transpose()[0]
        )

    def time_calculate_diff_uncertainty(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_uncertainty(
            non_varying.error.values.transpose(), varying.error.values.transpose()[0]
        )

    def time_data_array_mag(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_magnitude(non_varying.mag, varying.mag)

    def time_data_array_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_uncertainty(non_varying.error, varying.error)

    def time_average(self):
        data = self.data
        diff.average(data.mag.values, axis=1)

    def time_average_error(self):
        data = self.data
        diff.average_error(data.error.values, axis=1)

    def time_dataset_varying(self):
        data = self.data
        diff.dataset(data.groupby("varying"))

    def time_dataset_non_varying(self):
        data = self.non_varying
        diff.dataset(data.groupby("varying"))


class MemSuite(DifferentialSuite):
    def mem_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.magnitude(non_varying.mag.values, varying.mag.values)

    def mem_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.error(non_varying.error.values, varying.error.values)

    def mem_calculate_diff_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_magnitude(
            non_varying.mag.values.transpose(), varying.mag.values.transpose()[0]
        )

    def mem_calculate_diff_uncertainty(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_uncertainty(
            non_varying.error.values.transpose(), varying.error.values.transpose()[0]
        )

    def mem_data_array_mag(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_magnitude(non_varying.mag, varying.mag)

    def mem_data_array_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_uncertainty(non_varying.error, varying.error)

    def mem_average(self):
        data = self.data
        diff.average(data.mag.values, axis=1)

    def mem_average_error(self):
        data = self.data
        diff.average_error(data.error.values, axis=1)

    def mem_dataset_varying(self):
        data = self.data
        diff.dataset(data.groupby("varying"))

    def mem_dataset_non_varying(self):
        data = self.non_varying
        diff.dataset(data.groupby("varying"))


class PeakMemSuite(DifferentialSuite):
    def peakmem_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.magnitude(non_varying.mag.values, varying.mag.values)

    def peakmem_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.error(non_varying.error.values, varying.error.values)

    def peakmem_calculate_diff_magnitude(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_magnitude(
            non_varying.mag.values.transpose(), varying.mag.values.transpose()[0]
        )

    def peakmem_calculate_diff_uncertainty(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.calculate_differential_uncertainty(
            non_varying.error.values.transpose(), varying.error.values.transpose()[0]
        )

    def peakmem_data_array_mag(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_magnitude(non_varying.mag, varying.mag)

    def peakmem_data_array_error(self):
        varying = self.varying
        non_varying = self.non_varying
        diff.data_array_uncertainty(non_varying.error, varying.error)

    def peakmem_average(self):
        data = self.data
        diff.average(data.mag.values, axis=1)

    def peakmem_average_error(self):
        data = self.data
        diff.average_error(data.error.values, axis=1)

    def peakmem_dataset_varying(self):
        data = self.data
        diff.dataset(data.groupby("varying"))

    def peakmem_dataset_non_varying(self):
        data = self.non_varying
        diff.dataset(data.groupby("varying"))
