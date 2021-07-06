import enlighten

import differential_photometry.config as config

# Best candidate to make into a class.


def init_progress_bars():
    config.pbar_man = enlighten.get_manager(
    )  # set up universal progress bar manager

    config.pbar_status = config.pbar_man.status_bar(
        status_format=u'{fill}Stage: {demo}{fill}{elapsed}',
        color='bold_underline_bright_white_on_lightslategray',
        justify=enlighten.Justify.CENTER,
        demo='Processing file',
        autorefresh=True,
        min_delta=0.5)


def get_progress_bar(name: str,
                     total: int,
                     desc: str,
                     unit: str,
                     leave: bool,
                     color: str = None):
    if name in config.pbars.keys():
        pbar = config.pbars[name]
        pbar.close()

    pbar = config.pbar_man.counter(total=total,
                                   desc=desc,
                                   unit=unit,
                                   leave=leave,
                                   color=color)
    config.pbars[name] = pbar
    return pbar


def close_progress_bars():
    for name, pbar in config.pbars.items():
        pbar.close()
    config.pbars.clear()