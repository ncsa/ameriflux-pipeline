# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os.path
# NOTES 18
from netCDF4 import Dataset, num2date
import logging

from utils.process_validation import DataValidation
import utils.data_util as data_util

# create log object with current module name
log = logging.getLogger(__name__)


class OutputFormat:
    """
       Class to implement formatting of PyFluxPro output .nc file as per guide for Ameriflux submission
    """

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_file, file_meta_data_file, erroring_variable_flag, erroring_variable_key):
        """
        Method to implement data formatting for PyFluxPro output. Calls other methods.

        Args:
            input_file (str): A file path for the input data. This is the PyFluxPro input excel sheet
            file_meta_data_file (str) : Path for the file containing the meta data, typically the first line of Met data
            erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) have
                                        been renamed to Ameriflux labels. Y is renamed, N if not. By default it is N.
            erroring_variable_key (str): Variable name key used to match the original variable names to Ameriflux names
                                        for variables throwing an error in PyFluxPro L1.
                                        This is an excel file named L1_erroring_variables.xlsx
        Returns:
            obj: Pandas DataFrame object formatted for Ameriflux
            filename (str): Filename for writing the dataframe to csv
        """
        if os.path.splitext(input_file)[1] != '.nc':
            log.error("Run output file not in netCDF format. .nc extension expected")
            return None, None
        try:
            l2 = Dataset(input_file, mode='r')  # read netCDF file
        except KeyError or IOError:
            log.error("Unable to read netCDF file %s", input_file)
            return None, None

        l2_keys = list(l2.variables.keys())
        # list of unwanted variables to be removed
        unwanted_variables = ['latitude', 'longitude', 'crs', 'station_name']
        l2_keys = [ele for ele in l2_keys if ele not in unwanted_variables]
        # remove QCFlag variables
        l2_keys = [ele for ele in l2_keys if not ele.endswith('_QCFlag')]

        # NOTES 16. Get time data
        if 'time' not in l2_keys:
            log.error("time variable not in L2 output")
            return None, None
        time_var = l2.variables['time']
        time_units = time_var.units
        time = time_var[:]
        time = num2date(time, units=time_units, calendar='gregorian')  # calendar can be 365_day / gregorian
        time_data = time.data
        if len(time_data) < 1:
            log.error("Check timestamp column in file %s", input_file)
            return None, None

        # create a dataframe
        df = pd.DataFrame({'TIMESTAMP': [t.isoformat() for t in time_data]})
        # NOTES 16
        # insert TIMESTAMP_START and TIMESTAMP_END
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        # set timestamp as timestamp_start
        # shift timestamp 30min ahead and store in timestamp_end. step 1 in guide
        df.insert(1, 'TIMESTAMP_START', df['TIMESTAMP'])
        df.insert(2, 'TIMESTAMP_END', df['TIMESTAMP'] + timedelta(minutes=30))
        # check if timestamp spans an entire year. Else throw a warning. Step 6 in guide
        start_timestamp = df['TIMESTAMP_START'].iloc[0]
        end_timestamp = df['TIMESTAMP_END'].iloc[-1]
        if not OutputFormat.check_timestamp_span(start_timestamp, end_timestamp):
            log.warning("Timestamp start and Timestamp end does not span the whole year")

        # format timestamp columns as per ameriflux standards. step 5 in guide
        timestamp_cols = ['TIMESTAMP_START', 'TIMESTAMP_END']
        for col in timestamp_cols:
            df[col] = df[col].map(lambda t: t.strftime('%Y%m%d%H%M'))
        # drop additional time columns
        df.drop(columns=['TIMESTAMP'], inplace=True)

        # add met data to dataframe
        for var_name in l2_keys:
            df[var_name] = l2.variables[var_name][:].flatten()
            # convert to numeric and round to 3 decimal points
            df[var_name] = df[var_name].apply(pd.to_numeric, errors='coerce')
            df[var_name] = df[var_name].round(decimals=3)

        # drop columns if exists
        # step 2 in guide
        df.drop(columns=['CO2_SIGMA', 'H2O_SIGMA'], errors='ignore', inplace=True)

        # rename the erroring variables back to Ameriflux-friendly variables
        # convert erroring variables as a dictionary
        if erroring_variable_flag.lower() in ['n', 'no']:
            # if user chose not to replace the variable name, read the name mapping
            erroring_variable_key = pd.read_excel(erroring_variable_key)  # read L1 erroring variable name matching file
            if DataValidation.is_valid_erroring_variables_key(erroring_variable_key):
                # strip column names of extra spaces and convert to lowercase
                erroring_variable_key.columns = erroring_variable_key.columns.str.strip().str.lower()
                ameriflux_col = erroring_variable_key.filter(regex="ameriflux").columns.to_list()
                pyfluxpro_col = erroring_variable_key.filter(regex="pyfluxpro").columns.to_list()
                if ameriflux_col and pyfluxpro_col:
                    erroring_variable_key['Ameriflux label'] = erroring_variable_key[ameriflux_col[0]]
                    erroring_variable_key['PyFluxPro label'] = erroring_variable_key[pyfluxpro_col[0]]
                    column_labels = dict(zip(erroring_variable_key['PyFluxPro label'],
                                             erroring_variable_key['Ameriflux label']))
                    df.rename(columns=column_labels, inplace=True)
            else:
                log.warning("L1 Erroring Variables.xlsx file invalid format. Proceeding without replacing label")

        # drop additional time columns
        df.drop(columns=['time'], inplace=True)
        # fill all empty cells with -9999
        df.replace(np.nan, '-9999', inplace=True)
        df.replace('-9999.0', '-9999', inplace=True)
        # create the filename used for Ameriflux submission
        # read file_meta
        file_meta = data_util.read_csv_file(file_meta_data_file)
        # get the site name from dataframe
        file_site_name = file_meta.iloc[0][5]
        site_name = data_util.get_site_name(file_site_name)
        ameriflux_site_name = OutputFormat.get_ameriflux_site_name(site_name)
        start_time = df['TIMESTAMP_START'].iloc[0]
        end_time = df['TIMESTAMP_END'].iloc[-1]
        ameriflux_file_name = 'US-Ui' + str(ameriflux_site_name) + '_HH_' + str(start_time) + '_' + str(end_time)

        # return processed dataframe and ameriflux filename
        return df, ameriflux_file_name

    @staticmethod
    def check_timestamp_span(start, end):
        """
        Check if the timestamp spans the entire year from Jan 01 00:00 to Dec 31 23:30
        Args:
            start (datetime): Starting timestamp of data
            end (datetime): Ending timestamp of data
        Returns:
            bool: True if data spans the entire year, False if not.
        """
        start_year, start_month, start_day, start_hour, start_minute = \
            start.year, start.month, start.day, start.hour, start.minute
        end_year, end_month, end_day, end_hour, end_minute = end.year, end.month, end.day, end.hour, end.minute
        if start_year != end_year:
            log.warning("Year in timestamp_start and timestamp_end does not match")
            return False
        elif start_month != 1:
            log.warning("Starting month not January")
            return False
        elif end_month != 12:
            log.warning("Ending month not December")
            return False
        elif start_day != 1:
            log.warning("Start day not 1")
            return False
        elif end_day != 31:
            log.warning("End day is not 31")
            return False
        elif start_hour != 0:
            log.warning("Starting hour not 00")
            return False
        elif end_hour != 23:
            log.warning("Ending hour not 23")
            return False
        elif start_minute != 0:
            log.warning("Starting minute not 00")
            return False
        elif end_minute != 30:
            log.warning("ending minute not 30")
            return False
        else:
            return True

    @staticmethod
    def get_ameriflux_site_name(site_name):
        """
        Get the ameriflux site name from the field site name.
        The Ameriflux sitename is typically characters (A, B, C, D or E)

        Args:
            site_name (str): field site name
        Returns:
            (str): matching ameriflux site name
        """
        if site_name == 'Sorghum':
            return 'E'
        elif site_name in ['Miscanthus-Basalt', 'Miscanthus-Control']:
            return 'B'
        elif site_name in ['Maize-Basalt', 'Maize-Control']:
            return 'C'
        elif site_name == 'Switchgrass':
            return 'A'
