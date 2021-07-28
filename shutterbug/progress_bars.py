from typing import Any

import functools
import enlighten

import numbers

# Best candidate to make into a class.
manager = None
status = None

progress_bars = {}

__indentation_to_colour = {0: "white", 1: "blue", 2: "purple"}


def init():
    global manager
    global status
    manager = enlighten.get_manager()  # set up universal progress bar manager

    status = manager.status_bar(
        status_format="{fill}Stage: {stage}{fill}{elapsed}",
        color="bold_underline_bright_white_on_lightslategray",
        justify=enlighten.Justify.CENTER,
        stage="Processing data",
        autorefresh=True,
        min_delta=0.1,
    )


def start(
    name: str,
    total: int,
    desc: str,
    unit: str,
    leave: bool = True,
    color: str = "white",
):
    global progress_bars
    pbar = get(name)
    if pbar is not None:
        pbar.close()

    pbar = manager.counter(total=total, desc=desc, unit=unit, leave=leave, color=color)
    progress_bars[name] = pbar
    return pbar


def progress(
    name: str,
    desc: str,
    unit: str,
    leave: bool,
    status_str: str,
    countable_var: Any = None,
    arg_pos: int = 0,
    indentation: int = 0,
):
    desc = "  " * indentation + desc

    def progress_decorator(func):
        global status

        @functools.wraps(func)
        def wrapper_progress(*args, **kwargs):
            pbar = get(name)
            if pbar is None:
                global status
                total = __get_len_from_args_kwargs(
                    countable_var, arg_pos, func.__name__, *args, **kwargs
                )
                color = __indentation_to_colour[indentation]
                pbar = start(name, total, desc, unit, leave, color)
                status.update(stage=status_str)
                pbar.refresh()

            result = func(*args, **kwargs)
            if pbar.count == pbar.total:
                close(name)
            else:
                pbar.update()
            return result

        return wrapper_progress

    return progress_decorator


def __get_len_from_args_kwargs(
    countable_var: Any, arg_pos: int, func_name: str, *args, **kwargs
):
    if countable_var in kwargs.keys():
        if isinstance(kwargs[countable_var], numbers.Number):
            total = kwargs[countable_var]
        else:
            total = len(kwargs[countable_var])
    else:
        try:
            total = len(args[arg_pos])
        except IndexError:
            raise ValueError(
                f"Improperly set up progress bar, unable to get total from function {func_name}"
            )
    if total == 0:
        raise ValueError(
            f"Improperly set up progress bar, unable to get total from function {func_name}"
        )
    return total


def get(name: str):
    global progress_bars
    if name in progress_bars.keys():
        return progress_bars[name]
    else:
        return None


def close_all():
    global progress_bars
    for pbar in progress_bars.values():
        pbar.close()
    progress_bars.clear()
    return True


def close(name: str):
    global progress_bars
    if name in progress_bars.keys():
        progress_bars[name].close()
        progress_bars.pop(name, None)
    return True


def update(pbar: enlighten.Counter, attr: str, update_to: Any):
    setattr(pbar, attr, update_to)
    pbar.refresh()
    return True
