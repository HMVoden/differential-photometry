import logging
from pathlib import PurePath

import astropy.units as u
import numpy as np
import pandas as pd


def extract_data(filename: str) -> pd.DataFrame:
    """ Assuming there are headers in the data file, this takes the filename opens it and reads it
    into a pandas dataframe, cleans the headers to make it all lowercase with no parenthesis and returns only
    the columns we're interested in.

    Keyword arguments:
    filename -- the name of the file to be opened and read
    """

    data_path = PurePath(filename)
    if data_path.suffix == '.xlsx':  # This way we can ignore if it's a csv or excel file
        df = pd.read_excel(data_path)
    else:
        df = pd.read_csv(data_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(
        '(', '_').str.replace(')', '').str.replace('<', '').str.replace('>', '')
    # Cleanup of headers, could be made more succinct with a simple REGEX
    desired_column_names = np.array(['obj',
                                     'name',
                                     'mag',
                                     'error',
                                     'error_t',
                                     's/n',
                                     'x',
                                     'y',
                                     'date',
                                     'time',
                                     'jd'])
    # We can input the desired column names as a variable, then issue info notices on what comes out.
    # As a possible improvement to this script.
    extracted_column_names = df.columns
    # Finds common column names
    intersection = np.intersect1d(desired_column_names, extracted_column_names)
    return clean_stars_data(df[intersection])


def extract_samples_stars(dataframe: pd.DataFrame) -> int:
    """Determines and returns the number of different star samples and number of stars as integers"""
    rows = dataframe.shape[0]
    if 'obj' in dataframe.columns:  # Since this is what we normally see in the .csvs
        num_stars = dataframe['obj'].nunique()
    elif 'name' in dataframe.columns:  # Backup in case of other Mira data
        num_stars = dataframe['name'].nunique()
    samples = int(rows/num_stars)
    return num_stars, samples


def clean_stars_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Ensures that the columns mag, error, error_t and either obj or name are present.
    Then makes sure that the mag, error and error_t are viable and in the right format.
    Removes all stars with any mag value of "Flux<0"

    Keyword Arguments:
    dataframe -- A pandas dataframe containing the proper column names
    """
    if 'obj' in dataframe.columns:
        dataframe = dataframe.rename(columns={'obj': 'name'})

    required_columns = ['mag', 'error', 'error_t']
    for col in required_columns:
        if col not in dataframe.columns:
            raise KeyError(
                "ERROR: Unable to continue program, missing critical column: {0}".format(col))
    if 'name' not in dataframe.columns and 'obj' not in dataframe.columns:
        raise KeyError("""ERROR: Unable to continue program, 
                    missing name/object columns for number of star
                    calculations""")

    datatypes = dataframe.dtypes
    if not (datatypes.mag.name == "float64"):  # Could make this apply to error and error_t too
        logging.warning(
            "Data column '{0}' is not a numerical type, attempting to fix".format("mag"))
        # First instance of bad data
        bad_mags = dataframe[(dataframe.mag == "Flux<0")]

        stars_removed = bad_mags.name.unique()
        star_rows = dataframe[(dataframe['name'].isin(stars_removed))]

        logging.warning(
            "Removing star(s) {0} from dataset".format(stars_removed))
        dataframe = dataframe.drop(index=star_rows.index)
        dataframe['mag'] = pd.to_numeric(dataframe['mag'])

    return dataframe
