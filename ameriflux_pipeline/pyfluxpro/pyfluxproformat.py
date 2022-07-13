# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np

from utils.process_validation import DataValidation


class PyFluxProFormat:
    '''
    Class to implement formatting of EddyPro full output as per guide
    '''

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_path):
        """
        Constructor for the class

        Args:
            input_path (str): A file path for the input data. This is the full output of EddyPro
        Returns:
            obj: Pandas DataFrame object.
        """
        df, df_meta = PyFluxProFormat.read_data(input_path)  # reads file and returns data and meta data
        # check for required columns in eddypro full output sheet
        is_valid = DataValidation.is_valid_full_output(df)
        if not is_valid:
            print("EddyPro full output not in valid format")
            return None
        # add columns and units to meta data if neccessary
        df, df_meta = PyFluxProFormat.add_timestamp(df, df_meta)  # step 3b in guide
        # convert -9999.0 to NaN. To make numerical conversions easier.
        df.replace('-9999.0', np.nan, inplace=True)
        df.replace('-9999', np.nan, inplace=True)

        # step 3c. Convert temp unit from K to C
        df, df_meta = PyFluxProFormat.convert_temp_unit(df, df_meta)
        # step 3d. Convert air pressure unit.
        df, df_meta = PyFluxProFormat.convert_airpressure_unit(df, df_meta)
        # step 3e is skipped with time-gap filling settings in eddypro. so is step3.e.a
        df = PyFluxProFormat.concat_df(df, df_meta)  # concatenate df and df meta
        if df is None:
            return None
        # convert NaNs back
        df.replace(np.nan, 'NAN', inplace=True)
        # return formatted df
        return df

    @staticmethod
    def read_data(path):
        """
        Reads data (This is the full output of EddyPro).
        Returns dataframe containing the met data and another df containing meta data

        Args:
            path(str): input data file path
        Returns:
            df (obj): Pandas DataFrame object
            df_meta (obj) : Pandas DataFrame object having the meta data
        """
        print("Reading EddyPro full output file ", path)
        df = pd.read_csv(path, skiprows=1)  # skip the first row so as to skip file_info row
        df_meta = df.head(1)  # the first row has the meta data. Row index 0 has the units of all variables
        df = df.iloc[1:, :]  # drop the first row of units. Will be concatenated with df_meta later
        df.reset_index(drop=True, inplace=True)  # reset index after dropping rows
        return df, df_meta

    @staticmethod
    def add_timestamp(df, df_meta):
        """
        Function to add TIMESTAMP column in df, as per step 3b in guide
        Add date and time column. Replace inplace - with /.
        Add new column and unit to meta dataframe
        Move TIMESTAMP column to index 1

        Args:
            df (object): Pandas DataFrame object
            df_meta (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
            df_meta (object): Processed Pandas DataFrame object
        """
        # create new column and unit for TIMESTAMP by adding date and time columns
        date_col = df.filter(regex="date|Date").columns.to_list()[0]
        time_col = df.filter(regex="time|Time").columns.to_list()[0]
        df['TIMESTAMP'] = df[date_col] + ' ' + df[time_col]
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        # NOTES 22
        # shift timestamp 30min behind to get the start time of the data
        df['TIMESTAMP'] = df['TIMESTAMP'] - pd.Timedelta(minutes=30)
        df_meta['TIMESTAMP'] = 'yyyy/mm/dd HH:MM'  # add new variable and unit to meta df
        # convert TIMESTAMP to string format
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.strftime('%Y/%m/%d %H:%M'))
        # move TIMESTAMP column to first index
        cols = list(df.columns)
        cols.insert(1, cols.pop(cols.index('TIMESTAMP')))  # pop and insert TIMESTAMP at index 1
        df = df.loc[:, cols]  # rearrange df
        df_meta = df_meta.loc[:, cols]
        return df, df_meta

    @staticmethod
    def convert_temp_unit(df, df_meta):
        """
        Method to change temperature measurement unit from kelvin to Celsius. Step 3c in guide.

        Args:
            df (object): Pandas DataFrame object
            df_meta (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
            df_meta (object): Processed Pandas DataFrame object
        """
        # convert string to numerical
        df['sonic_temperature'] = df['sonic_temperature'].astype(float)
        df['sonic_temperature_C'] = df.apply(lambda row: row.sonic_temperature - 273.15, axis=1)  # convert to celsius
        df['sonic_temperature_C'] = df['sonic_temperature_C'].round(3)  # round to 3 decimal places
        df_meta['sonic_temperature_C'] = '[C]'  # add new variable and unit to meta df
        return df, df_meta

    @staticmethod
    def convert_airpressure_unit(df, df_meta):
        """
        Method to change air pressure measurement unit from Pa to kPa. Step 3d in guide.

        Args:
            df (object): Pandas DataFrame object
            df_meta (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
            df_meta (object): Processed Pandas DataFrame object
        """
        df['air_pressure'] = df['air_pressure'].apply(pd.to_numeric, errors='coerce')  # convert string to numerical
        df['air_pressure_kPa'] = df['air_pressure']/1000
        df['air_pressure_kPa'].round(3)
        df_meta['air_pressure_kPa'] = '[kPa]'
        return df, df_meta

    @staticmethod
    def concat_df(df, df_meta):
        """
        Concatenates dataframes

        Args:
            df (obj): Pandas DataFrame object
            df_meta (obj) : Pandas DataFrame object having the meta data
        Returns:
            df (obj): Merged Pandas DataFrame object
        """
        # concat the meta df and df if number of columns is the same
        if df_meta.shape[1] == df.shape[1]:
            df = pd.concat([df_meta, df], ignore_index=True)
            return df
        else:
            print("Number of columns in met data {} not the same as number of columns in meta data {}".
                  format(df.shape[1], df_meta.shape[1]))
            return None
