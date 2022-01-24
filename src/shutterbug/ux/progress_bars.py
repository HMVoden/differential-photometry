from typing import Generator, Optional
from attr import define, field
import enlighten
from contextlib import contextmanager


@define
class ProgressBarManager:
    _manager: enlighten.Manager = field(init=False)
    _status: enlighten.StatusBar = field(init=False)
    _indentation: int = field(init=False, default=0)
    # constants
    _STATUS_FORMAT = "{fill}Stage: {stage}{fill}{elapsed}"
    _COLOR = "bold_underline_bright_white_on_lightslategray"
    _INDENTATION_TO_COLOR = {0: "white", 1: "blue", 2: "purple"}

    def __attrs_post_init__(self):
        self._manager = enlighten.get_manager()  # type: ignore
        self._status = self._manager.status_bar(
            status_format=self._STATUS_FORMAT,
            color=self._COLOR,
            justify=enlighten.Justify.CENTER,
            stage="Initializing",
            autorefresh=True,
            min_delta=0.1,
        )

    @contextmanager
    def new(
        self, desc: str, unit: str, total: int, stage: Optional[str] = None
    ) -> Generator[enlighten.Counter, None, None]:
        """Creates a context manager to handle a new progress bar

        Parameters
        ----------
        desc : str
            Description of progress bar, appears on the lefthand side of the
            bar
        unit : str
            Units the progress bar is in, appears on the righthand side of the
            bar
        total : int
            Total number of objects that are being iterated over
        stage : Optional[str]
            What stage the program is in. If not specified, stage does not
            update

        Returns
        -------
        Generator[enlighten.Counter, None, None]
            Progress bar ready to be used with a 'with' statement

        """

        bar = self._make_counter(desc=desc, unit=unit, total=total)
        self._indentation += 1
        if stage is not None:
            self._status.update(stage=stage)
        try:
            yield bar
        finally:
            bar.close()

    def _make_counter(self, desc: str, unit: str, total: int) -> enlighten.Counter:
        """Makes a progress bar at a specific indentation and colour

        Parameters
        ----------
        desc : str
            Description of progress bar
        unit : str
            Unit the progress bar is in
        total : int
            Total number of objects being iterated over

        Returns
        -------
        enlighten.Counter
            Progress bar ready for use

        """

        indentation = self._indentation
        color = self._INDENTATION_TO_COLOR[indentation]
        indented_desc = f"{' '*indentation}{desc}"
        bar = self._manager.counter(
            total=total, desc=indented_desc, unit=unit, color=color
        )
        bar.refresh()
        return bar  # type: ignore
