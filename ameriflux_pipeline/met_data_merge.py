# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import argparse
import re
import pandas as pd
import os
import shutil
import csv
from datetime import timedelta
import utils.data_util as data_util
from pandas.errors import ParserError


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
    with open(data_path, newline='') as f:
        reader = csv.reader(f)
        file_meta = next(reader)  # gets the first line - file meta data

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
       Function to preprocess the data.
       This method merges several .dat files into one csv file, sorts the file to have data between start and end dates

       Args:
           files (list(str)): List of filepath to read met data
           start_date (str): Start date for met data to be merged
           end_date (str): End date for met data to be merged
       Returns:
           (df): Pandas dataframe object - merged met data including units and meta data
           (str): First line of file - meta data of file
    """
    dfs = []  # list of dataframes for each file
    meta_dfs = []  # list of meta data from each file, column name and units
    for file in files:
        root = os.getcwd()
        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        directory_name = os.path.dirname(file)

        output_file = os.path.join(root, directory_name, filename + '.csv')
        input_file = os.path.join(root, directory_name, basename)
        # copy and rename
        shutil.copyfile(input_file, output_file)
        # get the df, first row of file meta data and df meta data of column names and units
        # TODO check if file_meta for each file is the same. Check if the site name is the same for all merging files
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
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    # NOTES 19
    end_date += timedelta(days=1)
    met_data = met_data[(met_data['TIMESTAMP_datetime'] >= start_date) & (met_data['TIMESTAMP_datetime'] <= end_date)]
    met_data.drop(columns=['TIMESTAMP_datetime'], inplace=True)
    # check if number of columns in met data and meta data are same
    if meta_df.shape[1] == met_data.shape[1]:
        df = pd.concat([meta_df, met_data], ignore_index=True)
        return df, file_meta
    else:
        print("Meta and data file columns not matching")
        return None, None


def main(files, start_date, end_date, output_file):
    """
       Main function to pre-process dat files. Calls other functions
       Args:
           files (list(str)): List of filepath to read met data
           start_date (str): Start date for met data to be merged
           end_date (str): End date for met data to be merged
           output_file (str): Full file path to write the merged csv
       Returns:
           None
    """
    df, file_meta = data_processing(files, start_date, end_date)
    # make file_meta and df the same length to read as proper csv
    num_columns = df.shape[1]
    for _ in range(len(file_meta), num_columns):
        file_meta.append(' ')
    file_meta_line = ','.join(file_meta)
    # write processed df to output path
    data_util.write_data(df, output_file)
    # Prepend the file_meta to the met data csv
    with open(output_file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(file_meta_line.rstrip('\r\n') + '\n' + content)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("Automatic merging of met files started")
    # get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", action="store", default=None, nargs='*', help=".dat files for merging")
    parser.add_argument("--start", action="store", default="2021-01-01", help="Start date for merging in yyyy-mm-dd")
    parser.add_argument("--end", action="store", default='2021-12-31', help="End date for merging in yyyy-mm-dd")
    parser.add_argument("--output", action="store",
                        default=os.path.join(os.getcwd(), "data", "master_met", "input", "Flux.csv"),
                        help="File path to write the output merged csv file")
    args = parser.parse_args()
    # Some data preprocessing
    files = []
    if args.data is None:
        # no data is given as argument. ask for data during runtime.
        num_files = input("Enter number of files to be merged : ")
        for i in range(int(num_files)):
            files.append(input("Enter full file path for file" + str(i+1) + " : "))
    else:
        # data argument is given as parameter
        if len(args.data) == 1:
            # if comma separated, args will be treated as one argument. split by comma.
            file = args.data[0]
            files = file.split(',')
        else:
            # if space separated, args will be treated as multiple arguments. replace comma with empty string
            files = [f.replace(',', ' ').strip() for f in args.data]
    # remove duplicate files
    files = list(set(files))
    start_date = str(args.start)
    end_date = str(args.end)
    output_file = str(args.output)
    # TODO : check if file exists. Check data validity of dates
    main(files, start_date, end_date, output_file)
