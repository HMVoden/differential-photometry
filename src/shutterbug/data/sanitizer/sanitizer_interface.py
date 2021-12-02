from abc import ABC, abstractmethod


class SanitizerInterface(ABC):
    @abstractmethod
    def sanitize(
        self,
        frame,
        primary_variables,
        numeric_variables,
        discard_variables,
        keep_variables,
        keep_duplicates,
    ):
        pass

    @abstractmethod
    def _clean_names(self, frame):
        pass

    @abstractmethod
    def _coerce_into_numeric(self, frame, numeric_variables):
        pass

    @abstractmethod
    def _discard_variables(self, frame, discard_variables):
        pass

    @abstractmethod
    def _keep_variables(self, frame, keep_variables):
        pass

    @abstractmethod
    def _remove_abnormal_count_variables(self, frame, primary_variables):
        pass

    @abstractmethod
    def _drop_duplicates(self, frame, primary_variables, keep_duplicates):
        pass

    @abstractmethod
    def _drop_nan(self, frame):
        pass
