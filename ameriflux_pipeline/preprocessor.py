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

    def __init__(self, input_path, output_path, missing_timeslot_threshold):
        """Constructor for the class

            Args:
                input_path (str): A file path for the input data.
                output_path (str): A file path for the output data.
                missing_time_threshold (int): Number of 30min timeslot threshold

            Returns:
            obj: Pandas DataFrame object.

        """
        self.data_path = input_path
        self.output_data_path = output_path
        self.missing_timeslot_threshold = missing_timeslot_threshold

    def read_data(self):
        """Reads data and returns dataframe

            Args: None

            Returns:
                obj: Pandas DataFrame object

        """
        self.df = pd.read_csv(self.data_path)
        return self.df

    def write_data(self):
        """Write the dataframe to csv file

            Args: None

        """
        self.df.to_csv(self.output_data_path, index=False)
        pass

    def sync_time(self):
        """Sync time by delaying by 30min

            Args: None

        """
        # convert string timedate to pandas datetime type and store in another column
        self.df['timestamp'] = pd.to_datetime(self.df['TIMESTAMP'])
        # shift each timestamp 30min behind and store in another column
        self.df['timestamp_sync'] = self.df['timestamp'] - timedelta(minutes=30)
        # timestamp_sync will be used for all further calculations
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
                if insert_num_rows > 96:
                    user_confirmation = input("Enter Y to insert", insert_num_rows, "rows. Else enter N")

                    if user_confirmation in ['Y', 'y', 'yes', 'Yes']:
                        # insert missing timestamps
                        end_timestamp = self.df['timestamp_sync'].iloc[i]
                        start_timestamp = end_timestamp - timedelta(minutes=30 * insert_num_rows)
                        print("inserting ", insert_num_rows, "rows between ", start_timestamp, end_timestamp)
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

    def data_preprocess(self):
        """Cleans and process the dataframe as per the guide

            Args: None

            Returns:
                obj: Pandas DataFrame object
        """
        # sync time
        self.sync_time()
        # check for missing timestamps
        self.df['timedelta'] = self.df['timestamp_sync'].diff().astype('timedelta64[m]')

        # create missing timestamps
        user_confirmation = self.insert_missing_timestamp()
        if user_confirmation == 'N':
            # user confirmed not to insert missing timestamps. Return to main program
            return self.df

        # Step 4 in guide
        self.df = self.df.replace('', 'NAN')  # replace empty cells with 'NAN'
        self.df = self.df.replace(np.nan, 'NAN', regex=True)  # replace NaN with 'NAN'

        # correct timestamp string format - step 1 in guide
        self.timestamp_format()

        return self.df

        pass
