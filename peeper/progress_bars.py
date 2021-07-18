from typing import Any
import enlighten

# Best candidate to make into a class.
manager = None
status = None

progress_bars = {}


def init_progress_bars():
    global manager
    global status
    manager = enlighten.get_manager()  # set up universal progress bar manager

    status = manager.status_bar(
        status_format=u"{fill}Stage: {demo}{fill}{elapsed}",
        color="bold_underline_bright_white_on_lightslategray",
        justify=enlighten.Justify.CENTER,
        demo="Processing file",
        autorefresh=True,
        min_delta=0.5,
    )


def bar_update_wrapper(
    progress_bar: enlighten.Counter, function, *args, **kwargs
) -> Any:
    result = function(*args, **kwargs)
    progress_bar.update()
    return result


def get_progress_bar(
    name: str, total: int, desc: str, unit: str, leave: bool, color: str = None
):
    global progress_bars
    if name in progress_bars.keys():
        pbar = progress_bars[name]
        pbar.close()

    pbar = manager.counter(total=total, desc=desc, unit=unit, leave=leave, color=color)
    progress_bars[name] = pbar
    return pbar


def close_progress_bars():
    global progress_bars
    for name, pbar in progress_bars.items():
        pbar.close()
    progress_bars.clear()
