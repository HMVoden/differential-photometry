import logging
from typing import Tuple

import pandas as pd


def dataset_reduce_area(
    frame: pd.DataFrame, reduce_by: Tuple[int, int], image_shape: Tuple[int, int]
) -> pd.DataFrame:
    logging.info(f"Reducing area by x: {reduce_by[0]}, y: {reduce_by[1]}")
    reduce_x, reduce_y = reduce_by
    image_max_x, image_max_y = image_shape
    if reduce_x < 0 or reduce_y < 0:
        raise ValueError("Cannot reduce by a negative number")
    if image_max_x < 0 or image_max_y < 0:
        raise ValueError("The target image cannot be smaller than 0")
    new_x_maximum = image_max_x - reduce_x
    new_x_minimum = 0 + reduce_x
    new_y_maximum = image_max_y - reduce_y
    new_y_minimum = 0 + reduce_y
    condition = (
        (frame["x"] <= new_x_maximum)
        & (frame["x"] >= new_x_minimum)
        & (frame["y"] <= new_y_maximum)
        & (frame["y"] >= new_y_minimum)
    )
    frame = frame[condition]
    logging.info("Dataset reduced")
    return frame
