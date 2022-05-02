# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import pathlib
import os

def write_data(df, output_data):
    """
        Write the dataframe to csv file

        Args:
            df (object): Pandas DataFrame object
            output_data (str): File path to save output data
        Returns:
            None
    """
    print("Write data to file ", output_data)
    df.to_csv(output_data, index=False)


def read_excel(file_path):
    """
        Read an excel sheet to dataframe

        Args:
            file_path (str): File path to read data
        Returns:
            df (object): Pandas DataFrame object
    """
    df = pd.read_excel(file_path)  # read excel file
    return df

def find_output_dir(file_path):
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