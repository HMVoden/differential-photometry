import shutterbug.photometry.detect.variation as variation


class StationarityTestFactory:  # this feels pointless
    _selection_dict = {
        "chisquared": variation.ChiSquareTest,
        "adfuller": variation.AugmentedDFullerTest,
        "kpss": variation.KPSSTest,
        "zivot_andrews": variation.ZivotAndrewsTest,
        "adf_gls": variation.ADFGLSTest,
    }

    def create_test(
        self,
        test_method: str,
        clip_data: bool,
        null: str,
        varying_flag: str,
        correct_offset: bool,
        p_value: float,
        test_dimension: str,
        **kwargs
    ):
        test_class = self._selection_dict[test_method]
        test_class = test_class(
            test_method=test_method,
            clip_data=clip_data,
            null=null,
            varying_flag=varying_flag,
            p_value=p_value,
            test_dimension=test_dimension,
            correct_offset=correct_offset,
            **kwargs,
        )
        return test_class
