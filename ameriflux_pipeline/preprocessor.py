# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import timedelta
import os
import utils.data_util as data_util

import warnings
warnings.filterwarnings("ignore")


class Preprocessor:
    '''
    Class to implement preprocessing of meteorological data as per guide
    This class also implements formatting of meteorological data for PyFluxPro.
    '''

    # main method which calls other functions
    @staticmethod
    def data_preprocess(input_met_path, input_precip_path, precip_lower, precip_upper,
                        missing_time_threshold, user_confirmation):
        """
        Cleans and process the dataframe as per the guide. Process dataframe inplace
        Returns processed df and file meta df which is used in eddyproformat.py

        Args:
            input_path (str): A file path for the input data.
            input_precip_path(str): A file path for the input precipitation data.
            precip_lower (int) : Lower threshold value for precipitation in inches
            precip_upper (int) : Upper threshold value for precipitation in inches
            missing_time_threshold (int): Number of missing timeslot threshold. Used for both met data and precip data
            user_confirmation (str) : User decision on whether to insert,
                                        ignore or ask during runtime in case of large number of missing timestamps
        Returns:
            df (obj): Pandas DataFrame object, processed df
            file_meta (obj) : Pandas DataFrame object, meta data of file
        """

        # read input meteorological data file
        # NOTE 1
        df, file_df_meta = Preprocessor.read_met_data(input_met_path)
        print("Data contains ", df.shape[0], "rows ", df.shape[1], "columns")

        # get meta data
        # NOTE 2
        df_meta, file_meta = Preprocessor.get_meta_data(file_df_meta)
        # NOTE 4
        df_meta = Preprocessor.add_U_V_units(df_meta)

        # Write file meta data to another file
        # TODO : this can be omitted.
        # The file meta data is passed as a df (file_meta) to eddyproformat. No need for writing to file.
        input_filename = os.path.basename(input_met_path)
        file_meta_data_filename = os.path.splitext(input_filename)[0] + '_file_meta.csv'
        # write file_df_meta to this path
        file_meta_data_file = os.path.join(os.getcwd(), "tests", "data", file_meta_data_filename)
        data_util.write_data(file_meta, file_meta_data_file)  # write meta data of file to file. One row.

        # read input precipitation data file
        df_precip = Preprocessor.read_precip_data(input_precip_path, precip_lower, precip_upper,
                                                  missing_time_threshold, user_confirmation)

        # change column data types
        df = Preprocessor.change_datatype(df)

        # NOTE 6
        # set new variables
        new_variables = []
        # sync time
        df, new_variables = Preprocessor.sync_time(df, new_variables)

        # check for missing timestamps. get timedelta between 2 rows and add as a new column
        df['timedelta'] = Preprocessor.get_timedelta(df['timestamp_sync'])
        # add the new column to new_variables
        new_variables.append('timedelta')

        # create missing timestamps
        # NOTE 7
        df, insert_flag = Preprocessor.insert_missing_timestamp(df, 'timestamp_sync', 30.0,
                                                                missing_time_threshold, user_confirmation)
        if insert_flag == 'N':
            # user confirmed not to insert missing timestamps. Return to main program
            print("Ignoring missing timestamps in met data. Return to main")
            return df

        # correct timestamp string format - step 1 in guide
        df = Preprocessor.timestamp_format(df)

        # step 5 in guide. Calculation of soil heat flux
        # TODO : test with old data (non-critical)
        if Preprocessor.soil_heat_flux_check(df):
            df['shf_1_Avg'] = Preprocessor.soil_heat_flux_calculation(df['shf_mV_Avg(1)'], df['shf_cal_Avg(1)'])

        # Step 6 in guide. Absolute humidity check
        df['Ah_fromRH'] = Preprocessor.AhFromRH(df['AirTC_Avg'], df['RH_Avg'])
        # add Ah_fromRH column and unit to df_meta
        Ah_fromRH_unit = 'g/m^3'
        df_meta['Ah_fromRH'] = Ah_fromRH_unit

        # Step 4 in guide
        df = Preprocessor.replace_empty(df)

        # NOTE 6
        # delete newly created temp variables
        df = Preprocessor.delete_new_variables(df, new_variables)

        # step 8 in guide - add precip data. join df and df_precip
        # NOTE 8
        df = pd.merge(df, df_precip, on='TIMESTAMP')
        # TODO : ask Bethany about timeframes extra in one dataset, either met or precip.
        # add precipitation unit mm to df_meta
        df_meta['Precip_IWS'] = 'mm'

        # step 7 in guide - calculation of shortwave radiation
        SW_unit = 'W/m^2'  # unit for shortwave radiation
        df['SW_out_Avg'] = df['SWUp_Avg']
        df_meta['SW_out_Avg'] = SW_unit  # add shortwave radiation units
        if 'albedo_Avg' not in df.columns:
            # calculate albedo_avg from shortwave out and shortwave in
            df['Albedo_Avg'] = df['SWUp_Avg'] / df['SWDn_Avg']
            df_meta['Albedo_Avg'] = SW_unit  # add shortwave radiation units

        # NOTE 2
        # concat the meta df and df if number of columns is the same
        if df_meta.shape[1] == df.shape[1]:
            df = pd.concat([df_meta, df], ignore_index=True)
        else:
            print("Meta and data file columns not matching")

        # return processed and merged df. should contain 81 columns
        return df, file_meta

    @staticmethod
    def read_met_data(data_path):
        """
        Reads data and returns dataframe containing the met data and another df containing meta data

        Args:
            data_path(str): input data file path
        Returns:
            df (obj): Pandas DataFrame object
            file_df_meta (obj) : Pandas DataFrame object
        """
        df = pd.read_csv(data_path, header=None)  # read file without headers.

        # process df to get meta data
        file_df_meta = df.head(3)
        # the first row contains the meta data of file. second and third row contains met variables and their units
        file_df_meta.fillna('', inplace=True)  # fill NaNs with empty string for ease of replace
        file_df_meta = file_df_meta.applymap(lambda x: x.replace('"', ''))  # strip off quotes from all values

        # process df to get met data
        df = df.iloc[1:, :]  # drop the first row in df as it is the file meta data
        df.reset_index(drop=True, inplace=True)  # reset index after dropping rows
        df = df.applymap(lambda x: x.replace('"', ''))
        df.columns = df.iloc[0]  # set column names
        df = df.iloc[3:, :]  # drop first and second row as it is the units and min and avg
        df.reset_index(drop=True, inplace=True)  # reset index after dropping rows
        return df, file_df_meta

    @staticmethod
    def get_meta_data(file_df_meta):
        """
        Method to get file meta data and df meta data from meta data.
        Meta data from file contains the file meta data, column names and corresponding units in 3 rows
        Returns the file meta data df and meteorological meta data.

        Args :
            file_df_meta (obj): pandas dataframe consisting of all meta data
        Returns :
            df_meta (obj) : meta data of met data. Consists of column names and units.
            file_meta (obj) : meta data of file. Consists of file name, field site, and crop.
        """
        file_meta = file_df_meta.head(1)
        # the first row contains meta data of file. Used to match the filename to soil key.
        # returned with the processed df
        df_meta = file_df_meta.iloc[1:, :]
        # second and third row contains meta data of met tower variables (column names and units)
        df_meta.columns = df_meta.iloc[0]
        df_meta.drop(df_meta.index[0], inplace=True)
        df_meta.reset_index(drop=True, inplace=True)  # reset index after dropping first row
        return df_meta, file_meta

    @staticmethod
    def add_U_V_units(df):
        """
        Add units for U_Avg and V_Avg measurements in df_meta

        Args:
            df (obj): Pandas DataFrame object
        Returns:
            df (obj): Processed pandas DataFrame object
        """
        if 'U_Avg' in df.columns:
            df['U_Avg'][0] = 'm/s'
        if 'V_Avg' in df.columns:
            df['V_Avg'][0] = 'm/s'
        return df

    @staticmethod
    def read_precip_data(data_path, precip_lower, precip_upper, missing_time_threshold, user_confirmation):
        """
        Reads precipitation data from excel file and returns processed dataframe.
        Precip data is read for every 5min and the values are in inches.
        Converts precip unit from inches to mm.

        Args:
            data_path (str): input data file path
            precip_lower (int) : Lower threshold value for precipitation in inches
            precip_upper (int) : Upper threshold value for precipitation in inches
            missing_timeslot_threshold (int): Value for missing timeslot threshold. used for insert_missing_time method
            user_confirmation (str) : Option to either insert or ignore missing timestamps
        Returns:
            obj: Pandas DataFrame object
        """
        df = pd.read_excel(data_path)  # read excel file
        df.drop(['Station'], axis=1, inplace=True)  # drop unwanted columns
        # TODO: Ask Bethany - if missing time threshold for precip data is ok to be same as met data
        # NOTE 5
        # perform qa qc checks for precip data
        df = Preprocessor.precip_qaqc(df, precip_lower, precip_upper, missing_time_threshold, user_confirmation)
        # convert precipitation from in to mm
        # TODO : import cf_units and use to convert units. / udunits
        df['Precipitation (mm)'] = df['Precipitation (in)'] * 25.4  # convert inches to millimeter
        df.drop(['Precipitation (in)'], axis=1, inplace=True)  # drop unwanted columns
        # convert 5min samples to 30min samples by taking the sum
        df = df.set_index('Date & Time (CST)')
        precip_series = pd.Series(df['Precipitation (mm)'], index=df.index)
        # resampling to 30min timeslots. 00-30 is summed and stored in 00min. (beginning of timestamp)
        # skipna False accounts for NaN in values. If NaN present, the 30min resample has value of NaN.
        precip_30 = precip_series.resample('30min').agg(pd.Series.sum, skipna=False)
        # rename columns and create a df from series
        df = pd.DataFrame({'TIMESTAMP': precip_30.index, 'Precip_IWS': precip_30.values})
        # convert datetime to string and change format to match that of met dataframe
        df['TIMESTAMP'] = df['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M')
        # replace / with - to match timestamp format of met data
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.replace('-', '/'))
        return df

    @staticmethod
    def precip_qaqc(df, precip_lower, precip_upper, missing_time_threshold, user_confirmation):
        """
        Function to preform QA/QC check on precip data.
        Check if there are missing timestamps and if the precip value is between precip_lower and precip_upper
        If there is a missing timestamp, insert 5min timestamps with NAN value.
        If precip value is not within limits, replace the value with NAN.

        Args:
            df (obj): input precip dataframe
            precip_lower (int) : Lower threshold value for precipitation in inches
            precip_upper (int) : Upper threshold value for precipitation in inches
            missing_timeslot_threshold (int): Value for missing timeslot threshold. used for insert_missing_time method
            user_confirmation (str) : Option to either insert or ignore missing timestamps
        Returns:
            obj (Pandas DataFrame object): processed and cleaned precip dataframe
        """
        # check timestamps, if present for every 5 min
        df['timedelta'] = Preprocessor.get_timedelta(df['Date & Time (CST)'])
        df, insert_flag = Preprocessor.insert_missing_timestamp(df, 'Date & Time (CST)', 5.0,
                                                                missing_time_threshold, user_confirmation)
        if insert_flag == 'N':
            # user confirmed not to insert missing timestamps.
            print("Ignoring missing timestamps in precip data")

        df.drop(['timedelta'], axis=1, inplace=True)
        # check precip values in between 0 and 0.2 in
        # get indexes where precip is greater than 0.2 or less than 0.
        invalid_indexes = df.index[(df['Precipitation (in)'] > precip_upper)].to_list()
        invalid_indexes.extend(df.index[(df['Precipitation (in)'] < precip_lower)].to_list())
        # replace precip value with NaN at invalid indexes
        for index in invalid_indexes:
            df['Precipitation (in)'].iloc[index] = np.nan
        # return cleaned df
        return df

    @staticmethod
    def change_datatype(df):
        """
        Change data types of all columns, except TIMESTAMP to numeric

        Args:
            df (object): Pandas DataFrame object
        Returns:
            obj: Pandas DataFrame object
        """
        cols = df.columns.drop('TIMESTAMP')
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')  # coerce will replace all non-numeric values with NaN
        return df

    @staticmethod
    def sync_time(df, new_variables):
        """
        Sync time by delaying by 30min

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
    def get_timedelta(timeseries):
        """
        Method to calculate time difference between two rows. Calculate timedelta from timeseries.
        Used for met data and precip data

        Args:
            timeseries (pd.Series): Input time series used to calculate timedelta
        Returns:
            time_delta (pd.Series): output
        """
        time_delta = timeseries.diff().astype('timedelta64[m]')
        return time_delta

    @staticmethod
    def insert_missing_timestamp(df, time_col, time_interval, missing_timeslot_threshold, user_confirmation):
        """
        Function to check and insert missing timestamps.
        Used for precip data and met data.

        Args:
            df (object): Input pandas DataFrame object
            time_col (str) : timestamp column name. Date & Time (CST) for precip and timestamp_sync for met data
            time_interval (float): Expected time interval between two timestamps. 5.0 for precip and 30.0 for met data
            missing_timeslot_threshold (int): Value for missing timeslot threshold
            user_confirmation (str) : Option to either insert or ignore missing timestamps
        Returns:
            obj, str: Pandas dataframe object and string for representing yes or no
        """
        # Check if number of missing timeslots are greater than a threshold.
        # If greater than threshold, insert or ignore according to user confirmation
        # return: string:'Y' / 'N' - denotes insert_flag to insert missing timestamps

        # if all TimeDelta is not time_interval, the below returns non-zero value
        if df.loc[df['timedelta'] != time_interval].shape[0]:
            # get the row indexes where TimeDelta!=30.0
            row_indexes = list(df.loc[df['timedelta'] != time_interval].index)

            # iterate through missing rows, create new df with empty rows and correct timestamps,
            # concat new and old dataframes
            for i in row_indexes[1:]:
                # ignore the first row index as it is always 0 (timedelta = NaN)
                df1 = df[:i]  # slice the upper half of df
                df2 = df[i:]  # slice the lower half of df

                # insert rows between df1 and df2. number of rows given by timedelta/timeinterval
                insert_num_rows = int(df['timedelta'].iloc[i] // time_interval) - 1
                # 48 slots in 24hrs(one day)
                # ask for user confirmation if more than 96 timeslots (2 days) are missing
                if insert_num_rows > missing_timeslot_threshold:
                    print(insert_num_rows, "missing timeslots found")
                    if user_confirmation in ['A', 'a', 'ASK', 'ask', 'Ask']:
                        print("Enter Y to insert", insert_num_rows, "rows. Else enter N")
                        insert_flag = input("Enter Y/N : ")
                    elif user_confirmation in ['Y', 'y', 'yes', 'YES', 'Yes']:
                        insert_flag = 'Y'
                    elif user_confirmation in ['N', 'n', 'no', 'NO', 'No']:
                        insert_flag = 'N'

                    if insert_flag in ['Y', 'y', 'yes', 'YES', 'Yes']:
                        # insert missing timestamps
                        end_timestamp = df2[time_col].iloc[0]
                        start_timestamp = df1[time_col].iloc[0]
                        print("inserting ", insert_num_rows, "rows between ", start_timestamp, "and ", end_timestamp)
                        # create a series of time_interval timestamps
                        if time_interval == 5.0:
                            freq = '5T'
                        elif time_interval == 30.0:
                            freq = '30T'
                        else:
                            print(time_interval, "is invalid")
                        timestamp_series = pd.date_range(start=start_timestamp, end=end_timestamp, freq=freq)

                        # create new dataframe with blank rows
                        new_df = pd.DataFrame(np.zeros([insert_num_rows, df1.shape[1]]) * np.nan, columns=df1.columns)
                        # populate timestamp with created timeseries
                        new_df.loc[:, time_col] = pd.Series(timestamp_series)
                        # concat the 3 df
                        df = pd.concat([df1, new_df, df2], ignore_index=True)

                    else:
                        # insert flag is No.
                        return df, 'N'

        return df, 'Y'

    @staticmethod
    def timestamp_format(df):
        """
        Function to convert datetime to string and correct timestamp format

        Args:
            df (object): Pandas DataFrame object
        Returns:
            obj: Pandas DataFrame object
        """
        # convert datetime to string, replace - with /
        df['TIMESTAMP'] = df['timestamp_sync'].map(lambda t: t.strftime('%Y-%m-%d %H:%M')) \
            .map(lambda t: t.replace('-', '/'))
        return df

    @staticmethod
    def soil_heat_flux_check(df):
        """
        Check if soil heat flux calculation is required. Check if shf_Avg(1) and shf_Avg(2) exists.
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
        """
        Additional calculation for soil heat flux if needed. Step 5 in guide
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
        """
        es calculation for absolute humidity

        Args:
            T (float): air temperature in celsius
        Returns:
            float: calculated T
        """
        es = 0.6106 * (17.27 * T / (T + 237.3))
        return es

    @staticmethod
    def AhFromRH(T, RH):
        """
        Absolute humidity from relative humidity and temperature

        Args:
            T (float): Air temperature in celsius
            RH (float): Relative humidity in percentage
        Returns:
            AhFromRH (float) : Absolute humidity in g/m3
        """
        VPsat = Preprocessor.es(T)
        vp = RH * VPsat / 100
        Rv = 461.5  # constant : gas constant for water vapour, J/kg/K
        AhFromRH = 1000000 * vp / ((T + 273.15) * Rv)
        return AhFromRH

    @staticmethod
    def replace_empty(df):
        """
        Function to replace empty and NaN cells

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
        """
        Method to delete newly created variables in df. Delete columns in place

        Args :
            df (object): Pandas DataFrame object
            new_variables (list): A list of newly created variables during the process
        Returns :
            obj: Pandas DataFrame Object
        """
        df.drop(new_variables, axis=1, inplace=True)
        return df
