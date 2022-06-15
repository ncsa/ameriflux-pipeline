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


def write_data(df, output_data):
    """
        Write the dataframe to csv file

        Args:
            df (object): Pandas DataFrame object
            output_data (str): File path to save output data
        Returns:
            None
    """
    print("Write data to csv file ", output_data)
    df.to_csv(output_data, index=False)


def read_excel(file_path):
    """
        Read an excel sheet to dataframe

        Args:
            file_path (str): File path to read data
        Returns:
            df (object): Pandas DataFrame object
    """
    print("Read excel file ", file_path)
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
        print(data, "Incorrect date format")
        return None

def get_variables_index(text, var_pattern):
    """
        Get all variables and start and end index for each variable from the pyfluxpro control file

        Args:
            text (obj): Pandas series with all variable lines from L1.txt or L2.txt
            var_pattern (str): Regex pattern to find the starting line for [Variables] section
        Returns:
            variables (obj) : Pandas series. This is a subset of the input dataframe with only variable names
            var_start_end (list): List of tuple, the starting and ending index for each variable
    """
    variables = text[text.str.contains(var_pattern)]
    var_start_end = []
    for i in range(len(variables.index) - 1):
        start_ind = variables.index[i]
        end_ind = variables.index[i + 1]
        var_start_end.append((start_ind, end_ind))
    # append the start and end index of the last variable
    var_start_end.append((end_ind, text.last_valid_index()+1))
    return variables, var_start_end
