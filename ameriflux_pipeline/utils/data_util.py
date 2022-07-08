# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import re
import pathlib
import os
from dateutil.parser import parse
import logging

# create log object with current module name
log = logging.getLogger(__name__)

def read_csv_file(file_path, **kwargs):
    """
        Read csv file to dataframe with optional arguments

        Args:
            file_path (str): File path to read data
        Returns:
            df (object): Pandas DataFrame object
    """
    log.info("Read csv file %s", file_path)
    df = pd.read_csv(file_path, **kwargs)  # read csv file
    return df

def write_data_to_csv(df, output_data):
    """
        Write the dataframe to csv file

        Args:
            df (object): Pandas DataFrame object
            output_data (str): File path to save output data
        Returns:
            None
    """
    log.info("Write data to csv file %s", output_data)
    df.to_csv(output_data, index=False)


def read_excel(file_path):
    """
        Read an excel sheet to dataframe

        Args:
            file_path (str): File path to read data
        Returns:
            df (object): Pandas DataFrame object
    """
    log.info("Read excel file %s", file_path)
    df = pd.read_excel(file_path)  # read excel file
    return df


def get_site_name(file_site_name):
    """
    From the input file site name, return the site name
    Args:
        file_site_name (str): file site name from file meta data, first row of input met file
    Returns:
        (str): matching site name
    """
    if re.match('^CPU:Maize_Control_*', file_site_name):
        return 'Maize-Control'
    elif re.match('^CPU:Maize_*', file_site_name):
        return 'Maize-Basalt'
    elif re.match('^CPU:Miscanthus_Control_*', file_site_name):
        return 'Miscanthus-Control'
    elif re.match('^CPU:Miscanthus_*', file_site_name):
        return 'Miscanthus-Basalt'
    elif re.match('^CPU:Sorghum_*', file_site_name):
        return 'Sorghum'


def get_directory(file_path):
    """
        find output directory

        Args:
            file_path (str): File path to read data
        Returns:
            dir (str): output directory name
    """
    path = pathlib.Path(file_path)
    dir = os.path.dirname(path)
    return dir


def get_valid_datetime(data):
    """
    Method to check if the string input date is in valid format recognizable by datetime
    Returns a valid datetime if valid string input, else returns None
    Args:
        data (str): Input date to check for validity. The date can be in any format
    Returns:
        parse (str): Parsed datetime converted to string. None if data is not valid.
    """
    try:
        return parse(data)
    except ValueError:
        log.error("%s Incorrect date format", data)
        return None
