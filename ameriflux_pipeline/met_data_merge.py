# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import argparse
import pandas as pd
import numpy as np
from collections import Counter
import os
import shutil
import csv
import re
from datetime import timedelta
from pandas.errors import ParserError
import logging
import sys

import utils.data_util as data_util
from utils.process_validation import DataValidation

# create and configure logger
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s : %(name)s - %(message)s',
                    handlers=[logging.FileHandler("met_merger.log"), logging.StreamHandler(sys.stdout)])
# create log object with current module name
log = logging.getLogger(__name__)


def validate_inputs(files, start_date, end_date, output_file):
    """
    Method to check if inputs are valid

    Args:
        files(list): input data files to merge
        start_date (str): start date for merger
        end_date (str): end date for merger
        output_file (str): output file path to write merged csv
    Returns:
        (bool): True if inputs are valid, False if not
    """
    # check if input files exists
    for f in files:
        if not DataValidation.path_validation(f, 'file'):
            log.error("%s path does not exist", f)
            return False
    # validate start date if it is user provided, not the default value of 9999-01-01
    if start_date != '9999-99-99' and not data_util.get_valid_datetime(start_date):
        return False
    # validate end date if it is user provided, not the default value of 9999-12-31
    if end_date != '9999-99-99' and not data_util.get_valid_datetime(end_date):
        return False
    if not DataValidation.path_validation(data_util.get_directory(output_file), 'dir'):
        log.error("%s path does not exists", data_util.get_directory(output_file))
        return False
    if not DataValidation.filetype_validation(output_file, '.csv'):
        log.error(".csv extension expected for file %s", output_file)
        return False
    # all validations done
    return True


def read_met_data(data_path):
    """
    Reads data and returns dataframe containing the met data and another df containing meta data

    Args:
        data_path(str): input data file path
    Returns:
        df (obj): Pandas DataFrame object - dataframe with met data
        file_meta (str): The first line of met file
        df_meta (obj) : Pandas DataFrame object
        site_name (str): Site name extracted from first line of met file
    """
    # read data using csv
    with open(data_path, newline='') as f:
        reader = csv.reader(f)
        file_meta = next(reader)  # gets the first line - file meta data

    # get met data in a dataframe
    try:
        # try to read data as a csv with separator ', ; or tab'
        df = data_util.read_csv_file(data_path, sep=',|;|\t', header=None, names=None, skiprows=1, quotechar='"',
                                     dtype='unicode', engine='python')
    except ParserError as e:
        try:
            # try to read data as a csv with separator None argument
            df = data_util.read_csv_file(data_path, sep=None, header=None, names=None, skiprows=1, quotechar='"',
                                         dtype='unicode', engine='python')
        except ParserError as e:
            log.error("Exception in reading %s : %s", data_path, e)
            return None, None, None, None

    # process df to get meta data - column names and units
    # the first row contains the meta data of file, which is skipped in read_csv.
    # second and third row contains met variables and their units
    df_meta = df.head(3)
    df_meta = df_meta.applymap(lambda x: str(x).replace('"', ''))  # strip off quotes from all values
    df_meta = df_meta.applymap(lambda x: str(x).replace('*', ''))
    if not DataValidation.is_valid_meta_data(df_meta):
        log.error("Met data not in valid format")
        return None, None, None, None
    df_meta.columns = df_meta.iloc[0]  # set column names
    df_meta = df_meta.iloc[1:, :]
    df_meta.reset_index(drop=True, inplace=True)  # reset index after dropping rows

    # process df to get met data
    df = df.applymap(lambda x: str(x).replace('"', ''))
    df = df.applymap(lambda x: str(x).replace('*', ''))
    df.columns = df.iloc[0]  # set column names
    # NOTES 20
    # rename certain columns
    col_labels = {}
    # find albedo column and rename
    albedo_col = df.filter(regex=re.compile('^albedo', re.IGNORECASE)).columns.to_list()
    if len(albedo_col) > 0:
        col_labels[albedo_col[0]] = 'Albedo_Avg'
    # find CM3Up or Solar_Wm2_Avg col and rename to SWDn_Avg
    # and CM3Dn columns and rename to SWDn and SWUp
    cm3up_col = df.filter(regex=re.compile('^CM[1-9]Up', re.IGNORECASE)).columns.to_list()
    if cm3up_col:
        col_labels[cm3up_col[0]] = 'SWDn_Avg'
    else:
        # check if Solar_Wm2_Avg is present
        solar_col = df.filter(regex=re.compile('^Solar_Wm[1-9]', re.IGNORECASE)).columns.to_list()
        if solar_col:
            col_labels[solar_col[0]] = 'SWDn_Avg'
    # find CM3Dn or Sw_Out_Avg col and rename to SWUp_Avg
    cm3dn_col = df.filter(regex=re.compile('^CM[1-9]Dn', re.IGNORECASE)).columns.to_list()
    if cm3dn_col:
        col_labels[cm3dn_col[0]] = 'SWUp_Avg'
    else:
        # check if Sw_Out_Avg is present
        sw_out_col = df.filter(regex=re.compile('^Sw_Out', re.IGNORECASE)).columns.to_list()
        if sw_out_col:
            col_labels[sw_out_col[0]] = 'SWUp_Avg'

    # find CG3Dn and CG3Up columns and rename to LWDn and LWUp
    cg3upco_col = df.filter(regex=re.compile('^CG[1-9]UpCo', re.IGNORECASE)).columns.to_list()
    if cg3upco_col:
        col_labels[cg3upco_col[0]] = 'LWDnCo_Avg'
    cg3dnco_col = df.filter(regex=re.compile('^CG[1-9]DnCo', re.IGNORECASE)).columns.to_list()
    if cg3dnco_col:
        col_labels[cg3dnco_col[0]] = 'LWUpCo_Avg'
    # search for string ending with CG3Up or starting with CG3Up_Avg
    cg3up_col = df.filter(regex=re.compile('CG[1-9]Up$|^CG[1-9]Up_Avg', re.IGNORECASE)).columns.to_list()
    if cg3up_col:
        col_labels[cg3up_col[0]] = 'LWDn_Avg'
    cg3dn_col = df.filter(regex=re.compile('^CG[1-9]Dn$|^CG[1-9]Dn_Avg', re.IGNORECASE)).columns.to_list()
    if cg3dn_col:
        col_labels[cg3dn_col[0]] = 'LWUp_Avg'

    # find NetTot_Avg or Net_Rad_Avg column and rename to Rn_Avg
    netto_col = df.filter(regex=re.compile('^NetTot', re.IGNORECASE)).columns.to_list()
    if netto_col:
        col_labels[netto_col[0]] = 'Rn_Avg'
    else:
        # check if Net_Rad_Avg is present
        net_rad_col = df.filter(regex=re.compile('^Net_?Rad', re.IGNORECASE)).columns.to_list()
        if net_rad_col:
            col_labels[net_rad_col[0]] = 'Rn_Avg'

    cnrtc_col = df.filter(regex=re.compile('^CNR[1-9]_?T_?C', re.IGNORECASE)).columns.to_list()
    if cnrtc_col:
        col_labels[cnrtc_col[0]] = 'CNRTC_Avg'
    cnrtk_col = df.filter(regex=re.compile('^CNR[1-9]_?T_?K', re.IGNORECASE)).columns.to_list()
    if cnrtk_col:
        col_labels[cnrtk_col[0]] = 'CNRTK_Avg'
    netrs_col = df.filter(regex=re.compile('^Rs_net', re.IGNORECASE)).columns.to_list()
    if netrs_col:
        col_labels[netrs_col[0]] = 'NetRs_Avg'
    netrl_col = df.filter(regex=re.compile('^Rl_net', re.IGNORECASE)).columns.to_list()
    if netrl_col:
        col_labels[netrl_col[0]] = 'NetRl_Avg'

    # rename columns
    df.rename(columns=col_labels, inplace=True)
    df_meta.rename(columns=col_labels, inplace=True)

    # change VWC to VWC1
    vwc_col = df.filter(regex=re.compile('^VWC_', re.IGNORECASE)).columns.to_list()
    if vwc_col:
        vwc_labels = {}
        for col in vwc_col:
            vwc_labels[col] = 'VWC1_' + col.split('_')[1] + '_Avg'
        df.rename(columns=vwc_labels, inplace=True)
        df_meta.rename(columns=vwc_labels, inplace=True)
    # change TC to TC1
    tc_col = df.filter(regex=re.compile('^TC_', re.IGNORECASE)).columns.to_list()
    if tc_col:
        tc_labels = {}
        for col in tc_col:
            tc_labels[col] = 'TC1_' + col.split('_')[1] + '_Avg'
        df.rename(columns=tc_labels, inplace=True)
        df_meta.rename(columns=tc_labels, inplace=True)

    # after renaming check if column names are unique
    if len(df.columns.to_list()) != len(df.columns.unique()):
        counter_1 = Counter(df.columns.to_list())
        counter_2 = Counter(df.columns.unique())
        counter_diff = counter_1 - counter_2
        log.error("Met data column names are not unique: {}".format(counter_diff))
        return None, None, None, None

    df = df.iloc[3:, :]  # drop first and second row as it is the units and min / avg
    df.reset_index(drop=True, inplace=True)  # reset index after dropping rows

    # get the site name from file_meta
    file_site_name = file_meta[5]
    site_name = data_util.get_site_name(file_site_name)

    return df, file_meta, df_meta, site_name


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
    meta_dfs = []  # list of meta data from each file
    site_names = []

    for file in files:
        root = os.getcwd()
        basename = os.path.basename(file)
        filename = os.path.splitext(basename)[0]
        directory_name = os.path.dirname(file)
        # input files in .dat extension. Change to .csv extension
        output_file = os.path.join(root, directory_name, filename + '.csv')
        input_file = os.path.join(root, directory_name, basename)
        # copy and rename
        shutil.copyfile(input_file, output_file)
        df, file_meta, df_meta, site_name = read_met_data(output_file)
        if df is None:
            log.error("%s not readable", output_file)
            return None, None
        # check if the sites are the same for all metdata
        site_names.append(site_name)
        if len(set(site_names)) != 1:
            log.error("Data merge for different sites not recommended.")
            return None, None
        # all site names are the same. Append df to list
        dfs.append(df)
        meta_dfs.append(df_meta)

    # concat all dataframes in list
    met_data = pd.concat(dfs, axis=0, ignore_index=True)
    # replace empty string and string with only spaces with NAN
    met_data.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    meta_df = pd.concat(meta_dfs, axis=0, ignore_index=True)
    meta_df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    meta_df = meta_df.head(2)  # first 2 rows will give units and min/avg

    # get timestamp column
    timestamp_col = met_data.filter(regex=re.compile('TIMESTAMP', re.IGNORECASE)).columns.to_list()
    if not timestamp_col:
        log.error("No timestamp column found in met data")
        return None, None
    timestamp_col = timestamp_col[0]
    # get met data between start date and end date
    met_data['TIMESTAMP_datetime'] = pd.to_datetime(met_data[timestamp_col])
    met_data = met_data.sort_values(by='TIMESTAMP_datetime')
    if start_date == '9999-99-99':
        # no start date specified. merge all data
        start_date = met_data['TIMESTAMP_datetime'].min()
    else:
        # convert user input start date to datetime object
        start_date = pd.to_datetime(start_date)  # 00:00 of start date
        # NOTES 19
        start_date += timedelta(minutes=30)  # shift 30min forward
    if end_date == '9999-99-99':
        # no end date specified. merge all data
        end_date = met_data['TIMESTAMP_datetime'].max()
    else:
        # convert user input end date to datetime object
        end_date = pd.to_datetime(end_date)  # 00:00 of end date. get records till 00:00 of the next day
        # NOTES 19
        end_date += timedelta(days=1)  # shift a day ahead which gives till 00:00 of next day
    if start_date != met_data['TIMESTAMP_datetime'].min():
        # filter met data between start date and end date
        met_data = met_data[(met_data['TIMESTAMP_datetime'] >= start_date) &
                            (met_data['TIMESTAMP_datetime'] <= end_date)]
    # drop duplicate timestamps
    met_data.drop_duplicates(subset='TIMESTAMP_datetime', keep='first', inplace=True)
    met_data.drop(columns=['TIMESTAMP_datetime'], inplace=True)
    # check if number of columns in met data and meta data are same
    if meta_df.shape[1] == met_data.shape[1]:
        df = pd.concat([meta_df, met_data], ignore_index=True)
        log.info("Met data merged from %s to %s", start_date, end_date)
        return df, file_meta
    else:
        log.error("Meta and data file columns not matching %d %d", meta_df.shape[1], met_data.shape[1])
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
    if df is not None:
        # make file_meta and df the same length to read as proper csv
        num_columns = df.shape[1]
        for _ in range(len(file_meta), num_columns):
            file_meta.append(' ')
        file_meta_line = ','.join(file_meta)
        # write processed df to output path
        data_util.write_data_to_csv(df, output_file)
        # Prepend the file_meta to the met data csv
        with open(output_file, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(file_meta_line.rstrip('\r\n') + '\n' + content)
        log.info("Merging of met files completed. Merged file %s", output_file)
    else:
        log.error('-' * 10 + "Data merge failed. Aborting" + '-' * 10)


if __name__ == '__main__':
    log.info('-' * 50)
    log.info("############# Process Started #############")
    log.info("Automatic merging of met files started")
    # get arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", action="store", default=None, nargs='*', help=".dat files for merging")
    # get the start date. default will be Jan 1 of the year in met data file
    parser.add_argument("--start", action="store", default="9999-99-99", help="Start date for merging in yyyy-mm-dd")
    # get the end date. default will be Dec 31 of the year in met data file
    parser.add_argument("--end", action="store", default='9999-99-99', help="End date for merging in yyyy-mm-dd")
    parser.add_argument("--output", action="store",
                        default=os.path.join(os.getcwd(), "data", "master_met", "input", "Flux.csv"),
                        help="File path to write the output merged csv file")
    args = parser.parse_args()
    # get list of files to be merged
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
    # check if file exists
    is_valid = validate_inputs(files, start_date, end_date, output_file)
    if is_valid:
        main(files, start_date, end_date, output_file)
    else:
        log.error('-' * 10 + "Inputs not valid. Data merge failed. Aborting" + '-' * 10)
