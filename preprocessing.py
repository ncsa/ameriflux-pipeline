import pandas as pd
import numpy as np
from datetime import datetime
import time

import warnings
warnings.filterwarnings("ignore")

class Preprocessor:

    def __init__(self, path):
        """
        Constructor for the class
        Might be needed to pass arguments during preprocessing steps
        """
        self.data_path=path

    def read_data(self):
        """
        Reads data and returns dataframe
        :return: dataframe
        """
        df = pd.read_csv(self.data_path)
        return df

    def data_preprocess(self,df):
        """
        Cleans and process the dataframe as per the guide
        Returns the processed dataframe
        :param df: input dataframe to be processed
        :return: df: processed dataframe
        """
        # shift the TIMESTAMP by one cell up as to sync the timestamps.
        df['TIMESTAMP'] = df['TIMESTAMP'].shift(-1)
        df = df[:-2]  # get all data except for the last 2 row

        # convert string timedate to pandas datetime type and store in another column
        df['timestamp'] = pd.to_datetime(df['TIMESTAMP'])
        # check for 30min interval using timedelta function
        df['TimeDelta'] = df['timestamp'].diff().astype('timedelta64[m]')
        # if all TimeDelta is not 30.0, the below returns non-zero value
        if df.loc[df['TimeDelta'] != 30.0].shape[0]:
            # get the row indexes where TimeDelta!=30.0
            row_indexes = df.loc[df['TimeDelta'] != 30.0].index[0]
            for row_index in row_indexes:
                df.loc[row_index - 1] = ['NAN'] * df.shape[1]  # adding a row
            df.index = df.index + 1  # shifting index
            df = df.sort_index()  # sorting by index

        # Step 4 in guide
        df = df.replace('', 'NAN')

        return df

        pass

    def write_data(self, df, name):
        """
        Write the dataframe to csv file
        :param df: input dataframe to be written to csv file
               name : filename
        :return: None
        """
        df.to_csv(name, index=False)
        pass
