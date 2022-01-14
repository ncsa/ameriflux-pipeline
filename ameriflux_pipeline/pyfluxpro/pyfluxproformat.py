import pandas as pd
import numpy as np

import warnings
warnings.filterwarnings("ignore")


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
        # add columns and units to meta data if neccessary
        df, df_meta = PyFluxProFormat.add_timestamp(df, df_meta)  # step 3b in guide
        # convert -9999.0 to NaN. To make numerical conversions easier.
        df.replace('-9999.0', np.nan, inplace=True)

        # step 3c. Convert temp unit from K to C
        df, df_meta = PyFluxProFormat.convert_temp_unit(df, df_meta)
        # step 3d. Convert air pressure unit.
        df, df_meta = PyFluxProFormat.convert_airpressure_unit(df, df_meta)
        # step 3e is skipped with time-gap filling settings in eddypro. so is step3.e.a
        df = PyFluxProFormat.concat_df(df, df_meta)  # concatenate df and df meta
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
        df['TIMESTAMP'] = df['date'] + ' ' + df['time']
        df_meta['TIMESTAMP'] = 'yyyy/mm/dd HH:MM'  # add new variable and unit to meta df
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.replace('-', '/'))
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
        df['sonic_temperature'] = df['sonic_temperature'].apply(pd.to_numeric, errors='coerce')
        df['sonic_temperature_C'] = df['sonic_temperature']-273.15  # convert to celsius
        df['sonic_temperature_C'].round(3)  # round to 3 decimal places
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
        df = pd.concat([df_meta, df], ignore_index=True)
        return df
