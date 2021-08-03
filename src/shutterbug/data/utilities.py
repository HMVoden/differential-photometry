import logging
from typing import List

import pandas as pd


def time_from_data(jd: List[float]) -> pd.DatetimeTZDtype:
    time = pd.to_datetime(jd, origin="julian", unit="D")
    unique_years = time.year.nunique()
    unique_months = time.month.nunique()
    unique_days = time.day.nunique()

    logging.info("Number of days found in dataset: %s", unique_days)
    logging.info("Number of months found in dataset: %s", unique_months)
    logging.info("Number of years found in dataset: %s", unique_years)

    return time
