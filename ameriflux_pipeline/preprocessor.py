# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

import warnings
warnings.filterwarnings("ignore")


class Preprocessor:

    # main method which calls other functions
    @staticmethod
    def data_preprocess(input_path, output_path, missing_time_threshold, meta_data_path):
        """Cleans and process the dataframe as per the guide
            Process dataframe inplace

            Args:
                input_path (str): A file path for the input data.
                output_path (str): A file path for the output data.
                missing_time_threshold (int): Number of 30min timeslot threshold

            Returns:
                obj: Pandas DataFrame object

        """
        # set new variables
        new_variables = []

        # read input data file
        df = Preprocessor.read_data(input_path)
        print("Data contains ", df.shape[0], "rows ", df.shape[1], "columns")

        # read meta data file
        df_meta = Preprocessor.read_meta_data_file(meta_data_path)

        # change column data types
        df = Preprocessor.change_datatype(df)

        # sync time
        df, new_variables = Preprocessor.sync_time(df, new_variables)

        # check for missing timestamps. create timedelta between 2 rows
        df, new_variables = Preprocessor.get_timedelta(df, new_variables)

        # create missing timestamps
        df, user_confirmation = Preprocessor.insert_missing_timestamp(df, missing_time_threshold)
        if user_confirmation == 'N':
            # user confirmed not to insert missing timestamps. Return to main program
            return df

        # correct timestamp string format - step 1 in guide
        df = Preprocessor.timestamp_format(df)

        # step 5 in guide. Calculation of soil heat flux
        # TODO : test with old data
        if Preprocessor.soil_heat_flux_check(df):
            df['shf_1_Avg'] = Preprocessor.soil_heat_flux_calculation(df['shf_mV_Avg(1)'], df['shf_cal_Avg(1)'])

        # Step 6 in guide. Absolute humidity check
        df['Ah_fromRH'] = Preprocessor.AhFromRH(df['AirTC_Avg'], df['RH_Avg'])
        # df['Ah_fromRH'] = df.apply(lambda x: Preprocessor.AhFromRH( df['AirTC_Avg'], df['RH_Avg'] ), axis=1 )
        # add Ah_fromRH column and unit to df_meta
        Ah_fromRH_unit = 'g/m^3'
        df_meta['Ah_fromRH'] = Ah_fromRH_unit

        # Step 4 in guide
        df = Preprocessor.replace_empty(df)

        # delete newly created temp variables
        df = Preprocessor.delete_new_variables(df, new_variables)

        # step 7 in guide - calculation of shortwave radiation
        SW_unit = 'W/m^2'  # unit for shortwave radiation
        df['SW_out_Avg'] = df['SWUp_Avg']
        df_meta['SW_out_Avg'] = SW_unit  # add shortwave radiation units
        if 'albedo_Avg' not in df.columns:
            # calculate albedo_avg from shortwave out and shortwave in
            df['Albedo_Avg'] = df['SWUp_Avg'] / df['SWDn_Avg']
            df_meta['Albedo_Avg'] = SW_unit  # add shortwave radiation units

        # concat the meta df and df if number of columns is the same
        if df_meta.shape[1] == df.shape[1]:
            df = pd.concat([df_meta, df], ignore_index=True)
        else:
            print("Meta and data file columns not matching")

        # TODO: add precipitation data from IWS. Pending as data not available.

        # return processed df
        return df

    @staticmethod
    def read_data(data_path):
        """Reads data and returns dataframe

            Args:
                data_path(str): input data file path

            Returns:
                obj: Pandas DataFrame object

        """
        df = pd.read_csv(data_path)

        return df

    @staticmethod
    def read_meta_data_file(meta_data_path):
        """Method to read meta data csv file. Meta data file contains the column names and corresponding units. 2 rows.
            Returns the df

            Args :
                meta_data_path (str): meta data file path

            Returns :
                obj : pandas dataframe object of the read meta data csv

        """
        df_meta = pd.read_csv(meta_data_path)

        return df_meta

    @staticmethod
    def write_data(df, output_data_path):
        """Write the dataframe to csv file

            Args:
                df (object): Pandas DataFrame object
                output_data_path (str): File path to save output data

            Returns:
                None

        """
        df.to_csv(output_data_path, index=False)

        return

    @staticmethod
    def change_datatype(df):
        """Change datatypes of all columns, except TIMESTAMP to numeric

            Args:
                df (object): Pandas DataFrame object

            Returns:
                obj: Pandas DataFrame object

        """
        cols = df.columns.drop('TIMESTAMP')
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        print(df.info())

        return df

    @staticmethod
    def data_ok(value):
        """Logical function to test if a variable is a number or not.
            Currently not used as data types are changed for all columns except TIMESTMAP

            Args:
                value: variable

            Returns:
                bool : true or false

        """
        if (isinstance(value, int) or isinstance(value, float)) and value != -9999:
            return True
        else:
            print(value, "data not a number")
            return False

    @staticmethod
    def sync_time(df, new_variables):
        """Sync time by delaying by 30min

            Args:
                df (object): Input pandas DataFrame object
                new_variables (list): List of new variables

            Returns:
                obj, list: Pandas DataFrame object and list of variables

        """
        # convert string timedate to pandas datetime type and store in another column
        df['timestamp'] = pd.to_datetime(df['TIMESTAMP'])

        # shift each timestamp 30min behind and store in another column
        df['timestamp_sync'] = df['timestamp'] - timedelta(minutes=30)

        # add the newly created columns to new_variables
        new_variables.append('timestamp')
        new_variables.append('timestamp_sync')

        return df, new_variables

    @staticmethod
    def get_timedelta(df, new_variables):
        """Method to calculate time difference between two rows. Calculate timedelta and create new column 'timedelta'

            Args:
                df (object): Input pandas DataFrame object
                new_variables (list): List of new variables

            Returns:
                obj, list: Pandas DataFrame object and list of variables

        """
        df['timedelta'] = df['timestamp_sync'].diff().astype('timedelta64[m]')

        # add the new column to new_variables
        new_variables.append('timedelta')

        return df, new_variables

    @staticmethod
    def insert_missing_timestamp(df, missing_timeslot_threshold):
        """function to check and insert missing timestamps

            Args:
                df (object): Input pandas DataFrame object
                missing_timeslot_threshold (int): Value for missing timeslot threshold

            Returns:
                obj, str: Pandas dataframe object and string for representing yes or no

        """
        # Check if number of missing timeslots are greater than a threshold.
        # If greater than threshold, ask for user confirmation and insert missing timestamps
        # :return: string:'Y' / 'N' - denotes user confirmation to insert missing timestamps

        # if all TimeDelta is not 30.0, the below returns non-zero value
        if df.loc[df['timedelta'] != 30.0].shape[0]:
            # get the row indexes where TimeDelta!=30.0
            row_indexes = list(df.loc[df['timedelta'] != 30.0].index)

            # iterate through missing rows, create new df with empty rows and correct timestamps,
            # concat new and old dataframes
            for i in row_indexes[1:]:
                # ignore the first row index as it is always 0 (timedelta = NaN)
                df1 = df[:i]  # slice the upper half of df
                df2 = df[i:]  # slice the lower half of df

                # insert rows between df1 and df2. number of rows given by timedelta/30
                insert_num_rows = int(df['timedelta'].iloc[i]) // 30
                # 48 slots in 24hrs(one day)
                # ask for user confirmation if more than 96 timeslots (2 days) are missing
                if insert_num_rows > missing_timeslot_threshold:
                    print(insert_num_rows, "missing timeslots found")
                    print("Enter Y to insert", insert_num_rows, "rows. Else enter N")
                    user_confirmation = input("Enter Y/N : ")

                    if user_confirmation in ['Y', 'y', 'yes', 'Yes']:
                        # insert missing timestamps
                        end_timestamp = df['timestamp_sync'].iloc[i]
                        start_timestamp = end_timestamp - timedelta(minutes=30 * insert_num_rows)
                        print("inserting ", insert_num_rows, "rows between ", start_timestamp, "and ", end_timestamp)
                        # create a series of 30min timestamps
                        timestamp_series = pd.date_range(start=start_timestamp, end=end_timestamp, freq='30T')

                        # create new dataframe with blank rows
                        new_df = pd.DataFrame(np.zeros([insert_num_rows, df1.shape[1]]) * np.nan, columns=df1.columns)
                        # populate timestamp with created timeseries
                        new_df.loc[:, 'timestamp_sync'] = pd.Series(timestamp_series)
                        # concat the 3 df
                        df = pd.concat([df1, new_df, df2], ignore_index=True)

                    else:
                        # user input is No.
                        return df, 'N'

        return df, 'Y'

    @staticmethod
    def timestamp_format(df):
        """Function to convert datetime to string and correct timestamp format

            Args:
                df (object): Pandas DataFrame object

            Returns:
                obj: Pandas DataFrame object

        """
        # convert datetime to string, replace - with /
        df['TIMESTAMP'] = df['timestamp_sync'].map(lambda t: t.strftime('%Y-%m-%d %H:%M'))\
            .map(lambda t: t.replace('-', '/'))

        return df

    @staticmethod
    def soil_heat_flux_check(df):
        """Check if soil heat flux calculation is required
            Check if shf_Avg(1) and shf_Avg(2) exists.
            If yes, shf calculation is not required, return False
            If no, check if shg_mV_Avg exists. If yes, shf calculation is required, return True. Else return False

            Args:
                df (object): Pandas DataFrame object

            Returns:
                bool : True or False

        """
        if 'shf_Avg(1)' in df.columns and 'shf_Avg(2)' in df.columns:
            return False
        elif 'shg_mV_Avg' in df.columns:
            return True
        else:
            return False

    @staticmethod
    def soil_heat_flux_calculation(shf_mV, shf_cal):
        """Additional calculation for soil heat flux if needed. Step 5 in guide
            shf_Avg=[shf_mV]*[shf_cal]

            Args:
                shf_mV (float): soil heat flux calculation variable
                shf_cal (float): soil heat flux variable

            Returns:
                float: calculated soil heat flux

        """
        return shf_mV * shf_cal

    @staticmethod
    def es(T):
        """es calculation for absolute humidity

            Args:
                T (float): air temperature in celsius

            Returns:
                float: calculated T

        """
        es = 0.6106 * (17.27 * T / (T + 237.3))

        return es

    @staticmethod
    def AhFromRH(T, RH):
        """Absolute humidity from relative humidity and temperature

            Args:
                T (float): Air temperature in celsius
                RH (float): Relative humidity in percentage

            Returns:
                float : Absolute humidity in g/m3

        """
        VPsat = Preprocessor.es(T)
        vp = RH * VPsat / 100
        Rv = 461.5  # constant : gas constant for water vapour, J/kg/K
        AhFromRH = 1000000 * vp / ((T + 273.15) * Rv)

        return AhFromRH

    @staticmethod
    def replace_empty(df):
        """Function to replace empty and NaN cells

            Args:
                df (object): Pandas DataFrame object

            Returns :
                obj: Pandas DataFrame object
        """
        df = df.replace('', 'NAN')  # replace empty cells with 'NAN'
        df = df.replace(np.nan, 'NAN', regex=True)  # replace NaN with 'NAN'

        return df

    @staticmethod
    def delete_new_variables(df, new_variables):
        """Method to delete newly created variables in df. Delete columns in place

            Args :
                df (object): Pandas DataFrame object
                new_variables (list): A list of newly created variables during the process

            Returns :
                obj: Pandas DataFrame Object

        """
        df.drop(new_variables, axis=1, inplace=True)

        return df
