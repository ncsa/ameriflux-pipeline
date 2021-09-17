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

    def __init__(self, input_path, output_path, missing_timeslot_threshold, meta_data_path):
        """Constructor for the class

            Args:
                input_path (str): A file path for the input data.
                output_path (str): A file path for the output data.
                missing_time_threshold (int): Number of 30min timeslot threshold

            Returns:
            obj: Pandas DataFrame object.

        """
        self.data_path = input_path # path of data csv file
        self.output_data_path = output_path # path to write the processed meteorological data file
        self.missing_timeslot_threshold = missing_timeslot_threshold # threshold for number of missing timestamps
        self.meta_data_path = meta_data_path # path of meta data file for meteorological file

        # list to store newly created variables/columns in df
        self.new_variables = [] # these will be deleted after all preprocessing


    def read_data(self):
        """Reads data and returns dataframe

            Args: None

            Returns:
                obj: Pandas DataFrame object

        """
        self.df = pd.read_csv(self.data_path)
        return self.df


    def read_meta_data_file(self):
        """
        Method to read meta data csv file. Meta data file contains the column names and corresponding units. 2 rows.
        Returns the df
            Args : None
            Returns : df_meta (object) : pandas dataframe object of the read meta data csv
        """
        df_meta = pd.read_csv(self.meta_data_path)
        return df_meta


    def write_data(self):
        """Write the dataframe to csv file

            Args: None

        """
        self.df.to_csv(self.output_data_path, index=False)
        pass

    def change_datatype(self):
        """
        Change datatypes of all columns, except TIMESTAMP to numeric
            Args: None
            Returns: None
        """
        cols = self.df.columns.drop('TIMESTAMP')
        self.df[cols] = self.df[cols].apply(pd.to_numeric, errors='coerce')
        print(self.df.info())

    def data_ok(self, value):
        """
        Logical function to test if a variable is a number or not.
        Currently not used as data types are changed for all columns except TIMESTMAP
            Args:
                value: variable
            Returns:
                bool : true or false
        """
        if (isinstance(value, int) or isinstance(value, float)) and value!=-9999:
            return True
        else:
            print(value , "data not a number")
            return False


    def sync_time(self):
        """Sync time by delaying by 30min

            Args: None

        """
        # convert string timedate to pandas datetime type and store in another column
        self.df['timestamp'] = pd.to_datetime(self.df['TIMESTAMP'])
        # shift each timestamp 30min behind and store in another column
        self.df['timestamp_sync'] = self.df['timestamp'] - timedelta(minutes=30)
        # add the newly created columns to new_variables
        self.new_variables.append('timestamp')
        self.new_variables.append('timestamp_sync')
        pass


    def get_timedelta(self):
        """
        Method to calculate time difference between two rows. Calculate timedelta and create new column 'timedelta'
            Args : None
            Returns : None
        """
        self.df['timedelta'] = self.df['timestamp_sync'].diff().astype('timedelta64[m]')
        # add the new column to new_variables
        self.new_variables.append('timedelta')
        pass

    def insert_missing_timestamp(self):
        """function to check and insert missing timestamps

            Args: None

            Returns:
                str: A string for confirming yes or no

        """
        # Check if number of missing timeslots are greater than a threshold.
        # If greater than threshold, ask for user confirmation and insert missing timestamps
        # :return: string:'Y' / 'N' - denotes user confirmation to insert missing timestamps

        # if all TimeDelta is not 30.0, the below returns non-zero value
        if self.df.loc[self.df['timedelta'] != 30.0].shape[0]:
            # get the row indexes where TimeDelta!=30.0
            row_indexes = list(self.df.loc[self.df['timedelta'] != 30.0].index)

            # iterate through missing rows, create new df with empty rows and correct timestamps,
            # concat new and old dataframes
            for i in row_indexes[1:]:
                # ignore the first row index as it is always 0 (timedelta = NaN)
                df1 = self.df[:i]  # slice the upper half of df
                df2 = self.df[i:]  # slice the lower half of df

                # insert rows between df1 and df2. number of rows given by timedelta/30
                insert_num_rows = int(self.df['timedelta'].iloc[i]) // 30
                # 48 slots in 24hrs(one day)
                # ask for user confirmation if more than 96 timeslots (2 days) are missing
                if insert_num_rows > self.missing_timeslot_threshold:
                    print(insert_num_rows, "missing timeslots found")
                    print("Enter Y to insert", insert_num_rows, "rows. Else enter N")
                    user_confirmation = input("Enter Y/N : ")

                    if user_confirmation in ['Y', 'y', 'yes', 'Yes']:
                        # insert missing timestamps
                        end_timestamp = self.df['timestamp_sync'].iloc[i]
                        start_timestamp = end_timestamp - timedelta(minutes=30 * insert_num_rows)
                        print("inserting ", insert_num_rows, "rows between ", start_timestamp, "and ", end_timestamp)
                        # create a series of 30min timestamps
                        timestamp_series = pd.date_range(start=start_timestamp, end=end_timestamp, freq='30T')

                        # create new dataframe with blank rows
                        new_df = pd.DataFrame(np.zeros([insert_num_rows, df1.shape[1]]) * np.nan, columns=df1.columns)
                        # populate timestamp with created timeseries
                        new_df.loc[:, 'timestamp_sync'] = pd.Series(timestamp_series)
                        # concat the 3 df
                        self.df = pd.concat([df1, new_df, df2], ignore_index=True)

                    else:
                        # user input is No.
                        return 'N'

        return 'Y'

    def timestamp_format(self):
        """Function to convert datetime to string and correct timestamp format

            Args: None

        """
        # convert datetime to string, replace - with /
        self.df['TIMESTAMP'] = self.df['timestamp_sync'].map(lambda t: t.strftime('%Y-%m-%d %H:%M'))\
                                                        .map(lambda t: t.replace('-', '/'))

        return


    def soil_heat_flux_check(self):
        """
        Check if soil heat flux calculation is required
        Check if shf_Avg(1) and shf_Avg(2) exists.
        If yes, shf calculation is not required, return False
        If no, check if shg_mV_Avg exists. If yes, shf calculation is required, return True. Else return False
            Args: None
            Returns:
                bool : True or False
        """
        if 'shf_Avg(1)' in self.df.columns and 'shf_Avg(2)' in self.df.columns:
            return False
        elif 'shg_mV_Avg' in self.df.columns:
            return True
        else:
            return False


    def soil_heat_flux_calculation(self, shf_mV, shf_cal):
        """
        Additional calculation for soil heat flux if needed. Step 5 in guide
        shf_Avg=[shf_mV]*[shf_cal]
        Args:
                shf_mV (float): soil heat flux calculation variable
                shf_cal (float): soil heat flux variable

        Returns:
            shf_Avg (float): calculated soil heat flux
        """
        return shf_mV * shf_cal

    def es(self, T):
        """
        es calculation for absolute humidity
        Args:
                T (float): air temperature in celsius
        Returns:
            es (float): calculated T
        """
        es = 0.6106 * (17.27 * T / (T + 237.3))
        return es


    def AhFromRH(self, T, RH):
        """
        Absolute humidity from relative humidity and temperature
        Args:
                T (float): air temperature in celsius
                RH (float): relative humidity in percentage
        Returns:
            AhFromRH (float) : absolute humidity in g/m3
        """
        VPsat = self.es(T)
        vp = RH * VPsat / 100
        Rv = 461.5 # constant : gas constant for water vapour, J/kg/K
        AhFromRH = 1000000 * vp / ((T + 273.15) * Rv)

        return AhFromRH


    def replace_empty(self):
        """
        Function to replace empty and NaN cells
            Args: None
            Returns : None
        """
        self.df = self.df.replace('', 'NAN')  # replace empty cells with 'NAN'
        self.df = self.df.replace(np.nan, 'NAN', regex=True)  # replace NaN with 'NAN'


    def delete_new_variables(self):
        """
        Method to delete newly created variables in df. Delete columns in place
            Args : None
            Returns : None
        """
        self.df.drop(self.new_variables, axis=1, inplace=True)
        pass


    # main method which calls other functions
    def data_preprocess(self):
        """Cleans and process the dataframe as per the guide
            Process dataframe inplace
            Args: None

            Returns:
                obj: Pandas DataFrame object
        """
        # read meta data file
        df_meta = self.read_meta_data_file()

        # change column data types
        self.change_datatype()
        # sync time
        self.sync_time()
        # check for missing timestamps. create timedelta between 2 rows
        self.get_timedelta()

        # create missing timestamps
        user_confirmation = self.insert_missing_timestamp()
        if user_confirmation == 'N':
            # user confirmed not to insert missing timestamps. Return to main program
            return self.df

        # correct timestamp string format - step 1 in guide
        self.timestamp_format()

        # step 5 in guide. Calculation of soil heat flux
        ### TODO : test with old data
        if self.soil_heat_flux_check():
            self.df['shf_1_Avg'] = self.soil_heat_flux_calculation(self.df['shf_mV_Avg(1)'], self.df['shf_cal_Avg(1)'])

        # Step 6 in guide. Absolute humidity check
        self.df['Ah_fromRH'] = self.AhFromRH(self.df['AirTC_Avg'], self.df['RH_Avg'])
        #self.df['Ah_fromRH'] = self.df.apply(lambda x: self.AhFromRH( self.df['AirTC_Avg'], self.df['RH_Avg'] ), axis=1 )
        # add Ah_fromRH column and unit to df_meta
        Ah_fromRH_unit = 'g/m^3'
        df_meta['Ah_fromRH'] = Ah_fromRH_unit

        # Step 4 in guide
        self.replace_empty()

        # delete newly created temp variables
        self.delete_new_variables()

        # step 7 in guide - calculation of shortwave radiation
        SW_unit = 'W/m^2' # unit for shortwave radiation
        self.df['SW_out_Avg'] = self.df['SWUp_Avg']
        df_meta['SW_out_Avg'] = SW_unit # add shortwave radiation units
        if 'albedo_Avg' not in self.df.columns:
            # calculate albedo_avg from shortwave out and shortwave in
            self.df['Albedo_Avg'] = self.df['SWUp_Avg'] / self.df['SWDn_Avg']
            df_meta['Albedo_Avg'] = SW_unit # add shortwave radiation units

        # concat the meta df and df if number of columns is the same
        if df_meta.shape[1]==self.df.shape[1]:
            self.df = pd.concat([df_meta, self.df], ignore_index=True)
        else:
            print("Meta and data file columns not matching")

        ### TODO: add precipitation data from IWS. Pending as data not available.

        # return processed df
        return self.df

        pass