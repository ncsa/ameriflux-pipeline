# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import timedelta
from pandas.api.types import is_datetime64_any_dtype as is_datetime64
pd.options.mode.chained_assignment = None

from utils.process_validation import DataValidation
import utils.data_util as data_util


class MasterMetProcessor:
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
            input_met_path (str): A file path for the input data.
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
        df, file_df_meta = MasterMetProcessor.read_met_data(input_met_path)
        print("Input meteorological data contains {} rows and {} columns".format(df.shape[0], df.shape[1]))

        # get meta data
        # NOTE 2
        df_meta, file_meta = MasterMetProcessor.get_meta_data(file_df_meta)
        if df_meta is None:
            print("Please check met data file. Aborting")
            return None, None
        # NOTE 4
        df_meta = MasterMetProcessor.add_U_V_units(df_meta)

        # read input precipitation data file
        user_confirmation = user_confirmation.lower()
        df_precip = MasterMetProcessor.read_precip_data(input_precip_path, precip_lower, precip_upper,
                                                        missing_time_threshold, user_confirmation)
        if df_precip is None:
            print("Merging of precipitation data is not possible.")
        # change column data types
        df = MasterMetProcessor.change_datatype(df)

        # NOTE 6
        # set new variables
        new_variables = []
        # sync time
        df, new_variables = MasterMetProcessor.sync_time(df, new_variables)

        # check for missing timestamps. get timedelta between 2 rows and add as a new column
        df['timedelta'] = MasterMetProcessor.get_timedelta(df['timestamp_sync'])
        # add the new column to new_variables
        new_variables.append('timedelta')

        # create missing timestamps
        # NOTE 7
        df, insert_flag = MasterMetProcessor.insert_missing_timestamp(df, 'timestamp_sync', 30.0,
                                                                      missing_time_threshold, user_confirmation)
        if insert_flag == 'N':
            # user confirmed not to insert missing timestamps. Return to main program
            print("Ignoring missing timestamps in met data. Return to main")
            return df

        # correct timestamp string format - step 1 in guide
        df = MasterMetProcessor.timestamp_format(df)

        # step 5 in guide. Calculation of soil heat flux
        # TODO : test with old data (non-critical)
        if MasterMetProcessor.soil_heat_flux_check(df):
            try:
                shf_mV, shf_cal = df['shf_mV_Avg(1)'], df['shf_cal_Avg(1)']
                df['shf_1_Avg'] = MasterMetProcessor.soil_heat_flux_calculation(shf_mV, shf_cal)
            except KeyError:
                print("Soil heat flux calculation failed. Check if columns shf_mV_Avg(1) and shf_cal_Avg(1) exists.")

        # Step 6 in guide. Absolute humidity check
        try:
            T, RH = df['AirTC_Avg'], df['RH_Avg']
            df['Ah_fromRH'] = MasterMetProcessor.AhFromRH(T, RH)
            # add Ah_fromRH column and unit to df_meta
            Ah_fromRH_unit = 'g/m^3'
            df_meta['Ah_fromRH'] = Ah_fromRH_unit
        except KeyError:
            print("AhFromRH calculation failed. Check if columns 'AirTC_Avg' and 'RH_Avg' exists.")

        # Step 4 in guide
        df = MasterMetProcessor.replace_empty(df)

        # NOTE 6
        # delete temporarily created variables
        df = MasterMetProcessor.delete_new_variables(df, new_variables)

        if df_precip is not None:
            # step 8 in guide - add precip data. join df and df_precip
            # keep all met data and have NaN for precip values that are missing - left join with met data
            # throw a warning if there are extra timestamps in met data
            if (df.shape[0] > df_precip.shape[0]):
                # there are more records in met data
                print("Extra timestamps in met data. Joining precip with NaN value in extra timestamps")
            # NOTE 8
            df = pd.merge(df, df_precip, on='TIMESTAMP', how='left')
            # add precipitation unit mm to df_meta
            df_meta['Precip_IWS'] = 'mm'

        # step 7 in guide - calculation of shortwave radiation
        SW_unit = 'W/m^2'  # unit for shortwave radiation
        # NOTE 10
        # get shortwave in and shortwave out columns from two instrument data
        df_sw_columns = df.filter(regex="SW").columns.to_list()
        df_cm3_columns = df.filter(regex="CM3").columns.to_list()
        df_sw_columns = [c.lower() for c in df_sw_columns]
        df_cm3_columns = [c.lower() for c in df_cm3_columns]
        # set shortwave out
        if 'swup_avg' in df_sw_columns:
            shortwave_out = 'SWUp_Avg'
            df['SW_out_Avg'] = df[shortwave_out]
            df_meta['SW_out_Avg'] = SW_unit  # add shortwave radiation units
        elif 'cm3dn_Avg' in df_cm3_columns:
            shortwave_out = 'CM3Dn_Avg'
            df['SW_out_Avg'] = df[shortwave_out]
            df_meta['SW_out_Avg'] = SW_unit  # add shortwave radiation units

        albedo_col = df.filter(regex="Albedo|albedo|ALB").columns.to_list()
        if (not albedo_col) or (albedo_col[0] not in df.columns):
            # calculate albedo_avg from shortwave out and shortwave in
            if 'swdn_Avg' in df_sw_columns:
                shortwave_in = 'SWDn_Avg'
            elif 'cm3up_Avg' in df_cm3_columns:
                shortwave_in = 'CM3Up_Avg'
            try:
                if shortwave_in and shortwave_out:
                    # avoid zero division error
                    df[albedo_col[0]] = df.apply(lambda x: float(x[shortwave_out]) / float(x[shortwave_in])
                                              if float(x[shortwave_in]) != 0 else np.nan, axis=1)

                    df_meta[albedo_col[0]] = SW_unit  # add shortwave radiation units
            except NameError:
                print("Shortwave calculation failed. Check SW or CD3 columns in met data.")
        else:
            # albedo column is present in metdata. Add SWunit
            df_meta[albedo_col[0]] = SW_unit  # add shortwave radiation units

        # NOTE 2
        # concat the meta df and df if number of columns is the same
        if df_meta.shape[1] == df.shape[1]:
            df = pd.concat([df_meta, df], ignore_index=True)
        else:
            print("Number of columns in met data {} not the same as number of columns in meta data {}".
                  format(df.shape[1], df_meta.shape[1]))
            return None, None

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
        print("Read file", data_path)
        df = pd.read_csv(data_path, header=None, low_memory=False)  # read file without headers.

        # process df to get meta data
        # TODO : Check with Bethany if Min/Avg is to be checked for.
        file_df_meta = df.head(4)  # first four lines of file contains meta data
        # the first row contains the meta data of file. second and third row contains met variables and their units
        file_df_meta = file_df_meta.fillna('')  # fill NaNs with empty string for ease of replace
        file_df_meta = file_df_meta.applymap(lambda x: str(x).replace('"', ''))  # strip off quotes from all values

        # process df to get met data
        df = df.iloc[1:, :]  # drop the first row in df as it is the file meta data
        df.reset_index(drop=True, inplace=True)  # reset index after dropping rows
        df = df.applymap(lambda x: str(x).replace('"', ''))
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
        # TODO : Check meta_data format. At present the code checks for first 4 lines.
        # But even if the last line is not present, it is ok.
        # Need to check at which row the timestamp/ numerical data is starting.
        file_meta = file_df_meta.head(1)
        # the first row contains meta data of file. Used to match the filename to soil key.
        # returned with the processed df
        df_meta = file_df_meta.iloc[1:, :]
        if not DataValidation.is_valid_meta_data(df_meta):
            print("Meta data not in valid format")
            return None, None
        # second and third row contains meta data of met tower variables (column names and units)
        df_meta.columns = df_meta.iloc[0]
        df_meta.drop(index=df_meta.index[0], axis=0, inplace=True)
        df_meta.reset_index(drop=True, inplace=True)  # reset index after dropping first row
        df_meta = df_meta.head(1)  # dropping the last row of Min / Avg
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
            missing_time_threshold (int): Value for missing timeslot threshold. used for insert_missing_time method
            user_confirmation (str) : Option to either insert or ignore missing timestamps
        Returns:
            obj: Pandas DataFrame object
        """
        df = pd.read_excel(data_path)  # read excel file
        df = MasterMetProcessor.get_valid_precip_data(df)
        if df is None:
            print("Precipitation data not valid.")
            return None

        # NOTE 5
        # perform qa qc checks for precip data
        df = MasterMetProcessor.precip_qaqc(df, precip_lower, precip_upper, missing_time_threshold, user_confirmation)
        # convert precipitation from in to mm
        # TODO : import cf_units and use to convert units. / udunits
        df['Precipitation_mm'] = df['Precipitation_in'] * 25.4  # convert inches to millimeter
        df.drop(['Precipitation_in'], axis=1, inplace=True)  # drop unwanted columns
        # convert 5min samples to 30min samples by taking the sum
        df = df.set_index('Timestamp')
        precip_series = pd.Series(df['Precipitation_mm'], index=df.index)
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
    def get_valid_precip_data(df):
        """
        Method to check if the input dataframe containing precipitation data is in valid format.
        Checks for expected columns like Time and Precip columns, and expected datatypes for the columns
        Returns the processed df
        Args:
            df (obj): Pandas dataframe object to check for valid format
        Returns:
            df (object): Pandas dataframe object which is the valid precip data with required columns.
        """
        time_flag, precip_flag = False, False
        # check for timestamp and precip column
        precip_col = df.filter(regex='Precipitation|precipitation|Precip|precip|Rain|rain|IWS').columns.to_list()
        time_col = df.filter(regex='Date|Time|time|CST|timestamp|TIMESTAMP|Timestamp').columns.to_list()
        if not time_col:
            print("Timestamp column not present in Precipitation data.")
            return None
        if not precip_col:
            print("Precipitation column not present in Precipitation data.")
            return None

        # there are more than 1 column that matches timestamp.
        # Process the first column that matches the criteria and break
        for col in time_col:
            if is_datetime64(df[col]):
                # col is of type datetime
                df['Timestamp'] = df[col]
                time_flag = True
                break
            elif DataValidation.string_validation(df[col].iloc[df[col].first_valid_index()]):
                # parse only accepts str input. Check if the column type is string.
                df['Timestamp'] = df[col].apply(lambda x: data_util.get_valid_datetime(x))
                time_flag = True
                break

        # there are more than 1 column that matches precipitation. There could be precip in inches and mm.
        for col in precip_col:
            if DataValidation.float_validation(df[col].iloc[df[col].first_valid_index()]):
                if any(inch_unit in col for inch_unit in ['(in)', 'inches', '(inches)']):
                    df['Precipitation_in'] = df[col]
                    precip_flag = True
                    break
                elif any(mm_unit in col for mm_unit in ['(mm)', 'mm', 'millimeter', 'millimeters',
                                                        '(millimeter)', '(millimeters)']):
                    df['Precipitation_in'] = df[col] / 25.4  # convert mm to inches
                    precip_flag = True
                    break

        # all validations done
        if time_flag and precip_flag:
            return df[['Timestamp', 'Precipitation_in']]
        elif not time_flag:
            print("Precipitation timestamp not in correct format")
            return None
        elif not precip_flag:
            print("Precipitation values not in correct format")
            return None
        else:
            return None

    @staticmethod
    def precip_qaqc(df, precip_lower, precip_upper, missing_time_threshold, user_confirmation):
        """
        Function to preform QA/QC check on precip data.
        Check if there are missing timestamps and if the precip value is between precip_lower and precip_upper
        If there is a missing timestamp, insert 5min timestamps with NAN value.
        If precip value is not within limits, replace the value with NAN.

        Args:
            df (obj): input precip dataframe
            precip_lower (float) : Lower threshold value for precipitation in inches
            precip_upper (float) : Upper threshold value for precipitation in inches
            missing_time_threshold (int): Value for missing timeslot threshold. used for insert_missing_time method
            user_confirmation (str) : Option to either insert or ignore missing timestamps
        Returns:
            obj (Pandas DataFrame object): processed and cleaned precip dataframe
        """
        # check timestamps, if present for every 5 min
        df['timedelta'] = MasterMetProcessor.get_timedelta(df['Timestamp'])
        df, insert_flag = \
            MasterMetProcessor.insert_missing_timestamp(df, 'Timestamp', 5.0,
                                                        missing_time_threshold, user_confirmation)
        if insert_flag == 'N':
            # user confirmed not to insert missing timestamps.
            print("Ignoring missing timestamps in precip data")

        df.drop(['timedelta'], axis=1, inplace=True)
        # check precip values in between 0 and 0.2 in
        # get indexes where precip is greater than 0.2 or less than 0.
        invalid_indexes = df.index[(df['Precipitation_in'] > precip_upper)].to_list()
        invalid_indexes.extend(df.index[(df['Precipitation_in'] < precip_lower)].to_list())
        # replace precip value with NaN at invalid indexes
        for index in invalid_indexes:
            df['Precipitation_in'].iloc[index] = np.nan
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
        # there could be values like INF in met data. Replace with NAN
        df[cols] = df[cols].replace([np.inf, -np.inf], np.nan)
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
            # ignore the first row index as it is always 0 (timedelta = NaN)
            row_indexes = row_indexes[1:]
            # iterate through missing rows, create new df with empty rows and correct timestamps,
            # concat new and old dataframes
            # iterate in reverse so that indexes do not change
            for i in row_indexes[::-1]:
                df1 = df[:i]  # slice the upper half of df
                df2 = df[i:]  # slice the lower half of df

                # insert rows between df1 and df2. number of rows given by timedelta/timeinterval
                missing_num_rows = int(df2['timedelta'].iloc[0] // time_interval) - 1
                if missing_num_rows > 0:
                    # insert only if missing_num_rows is a positive integer.
                    # is there are duplicate timestamps, missing_num_rows is either negative or 0.
                    end_timestamp = df2[time_col].iloc[0]
                    start_timestamp = df1[time_col].iloc[-1]
                    print(missing_num_rows, "missing timeslot(s) found between", start_timestamp, "and", end_timestamp)
                    insert_flag = 'y'  # insert timestamps by default. This is changed by user_confirmation
                    # 48 slots in 24hrs(one day)
                    # ask for user confirmation if more than 96 timeslots (2 days) are missing
                    if missing_num_rows > missing_timeslot_threshold:
                        if user_confirmation in ['a', 'ask']:
                            print("Enter Y to insert", missing_num_rows, "rows. Else enter N")
                            insert_flag = input("Enter Y/N : ")
                        elif user_confirmation in ['y', 'yes']:
                            insert_flag = 'Y'
                        elif user_confirmation in ['n', 'no']:
                            insert_flag = 'N'

                    if insert_flag.lower() in ['y', 'yes']:
                        # insert missing timestamps
                        print("inserting", missing_num_rows, "row(s) between", start_timestamp, "and", end_timestamp)
                        # create a series of time_interval timestamps
                        if time_interval == 5.0:
                            freq = '5T'
                        elif time_interval == 30.0:
                            freq = '30T'
                        else:
                            print(time_interval, "is invalid")
                            return df, 'N'

                        timestamp_series = pd.date_range(start=start_timestamp, end=end_timestamp, freq=freq)

                        # create new dataframe with blank rows
                        new_df = pd.DataFrame(np.zeros([missing_num_rows, df1.shape[1]]) * np.nan, columns=df1.columns)
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
        VPsat = MasterMetProcessor.es(T)
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
