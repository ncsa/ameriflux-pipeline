# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import datetime
import os
import shutil
import csv

from config import Config as cfg
import utils.data_util as data_util

GENERATED_DIR = 'generated'

def read_met_data(data_path):
    """
    Reads data and returns dataframe containing the met data and another df containing meta data

    Args:
        data_path(str): input data file path
    Returns:
        df (obj): Pandas DataFrame object - dataframe with met data
        file_meta (str): The first line of met file
        df_meta (obj) : Pandas DataFrame object
    """
    # read data using csv
    try:
        with open(data_path, newline='') as f:
            reader = csv.reader(f)
            file_meta = next(reader)  # gets the first line - file meta data
    except:
        print("Error reading ", data_path)
        return None, None, None

    # get met data in a dataframe
    try:
        df = pd.read_csv(data_path, sep=',', header=None, names=None, skiprows=1, quotechar='"', low_memory=False)
    except ParserError as e:
        try:
            df = pd.read_csv(data_path, sep='\t', header=None, names=None, skiprows=1, quotechar='"', low_memory=False)
        except ParserError as e:
            try:
                df = pd.read_csv(data_path, sep=';', header=None, names=None, skiprows=1, quotechar='"',
                                 low_memory=False)
            except ParserError as e:
                print("Exception in reading ", data_path)
                return None, None, None

    # process df to get meta data - column names and units
    # the first row contains the meta data of file. second and third row contains met variables and their units
    df_meta = df.head(3)
    df_meta = df_meta.applymap(lambda x: str(x).replace('"', ''))  # strip off quotes from all values
    df_meta = df_meta.applymap(lambda x: str(x).replace('*', ''))
    df_meta.columns = df_meta.iloc[0]  # set column names
    df_meta = df_meta.iloc[1:, :]
    df_meta.reset_index(drop=True, inplace=True)  # reset index after dropping rows

    # process df to get met data
    df = df.applymap(lambda x: str(x).replace('"', ''))
    df = df.applymap(lambda x: str(x).replace('*', ''))
    df.columns = df.iloc[0]  # set column names
    df = df.iloc[3:, :]  # drop first and second row as it is the units and min / avg
    df.reset_index(drop=True, inplace=True)  # reset index after dropping rows

    return df, file_meta, df_meta


def data_processing(files, start_date, end_date):
    """
       Function to preprocess the data. This method merges several .dat files into one csv file, sorts the file to have data between start and end dates

       Args:
           files (list(str)): List of filepath to read met data
           start_date (str): Start date for met data to be merged
           end_date (str): End date for met data to be merged
       Returns:
          met_df, meta_df, file_meta (df): Pandas dataframe object - merged met data
           (df): Pandas dataframe object - meta data
           (str): First line of file - meta data of file
    """
    dfs = []  # list of dataframes for each file
    meta_dfs = []  # list of meta data from each file
    for file in files:
        root = os.getcwd()
        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        directory_name = os.path.dirname(file)

        output_file = os.path.join(root, directory_name, filename + '.csv')
        input_file = os.path.join(root, directory_name, basename)
        # copy and rename
        shutil.copyfile(input_file, output_file)
        df, file_meta, df_meta = read_met_data(output_file)
        dfs.append(df)
        meta_dfs.append(df_meta)
    # concat all dataframes in list
    met_data = pd.concat(dfs)
    meta_df = pd.concat(meta_dfs)
    meta_df = meta_df.head(2)  # first 2 rows will give units and min/avg

    # get met data between start date and end date
    met_data['TIMESTAMP_datetime'] = pd.to_datetime(met_data['TIMESTAMP'])
    met_data = met_data.sort_values(by='TIMESTAMP_datetime')
    met_data['date'] = met_data['TIMESTAMP_datetime'].dt.date
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    met_data = met_data[(met_data['date'] > start_date) & (met_data['date'] <= end_date)]
    met_data.drop(columns=['TIMESTAMP_datetime', 'date'], inplace=True)
    return met_data, meta_df, file_meta


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Main function to pre-process dat files and merge according to start and end dates

    # Some data preprocessing
    files = [str(f).strip() for f in cfg.MERGE_FILES.split(',')]
    start_date = str(cfg.START_DATE)
    end_date = str(cfg.END_DATE)

    file_flag = True  # flag to check if all file exists
    for file in files:
        if not os.path.exists(file):
            print(file, "does not exist")
            file_flag = False
            break
    if file_flag:
        df, meta_df, file_meta = data_processing(files, start_date, end_date)
        # write processed df to output path
        data_util.write_data(df, cfg.INPUT_MET)
        # Filename to write file meta data
        input_filename = os.path.basename(cfg.INPUT_MET)
        directory_name = os.path.dirname(os.path.dirname(cfg.INPUT_MET))
        file_meta_data_filename = os.path.splitext(input_filename)[0] + '_file_meta.csv'
        # write file_df_meta to this path
        file_meta_data_file = os.path.join(directory_name, GENERATED_DIR, file_meta_data_filename)
        # Write file meta data to another file
        data_util.write_data(file_meta, file_meta_data_file)  # write meta data of file. One row.


