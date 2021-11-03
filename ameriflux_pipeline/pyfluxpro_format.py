import pandas as pd

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
        df, df_meta = PyFluxProFormat.read_data(input_path) # reads file and returns data and meta data
        # add columns and units to meta data if neccessary
        df, df_meta= PyFluxProFormat.add_timestamp(df, df_meta) # step 3b in guide
        df = PyFluxProFormat.concat_df(df, df_meta)



    @staticmethod
    def read_data(path):
        """
        Reads data and returns dataframe containing the met data and another df containing meta data
        Args:
            path(str): input data file path
        Returns:
            df (obj): Pandas DataFrame object
            df_meta (obj) : Pandas DataFrame object having the meta data
        """
        df = pd.read_csv(path, skiprows=1)  # skip the first row so as to skip file_info row
        df_meta = df.head(1) # the first row has the meta data. Row index 0 has the units of all variables
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
        df_meta['TIMESTAMP'] = 'yyyy/mm/dd HH:MM'
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.replace('-', '/'))
        # move TIMESTAMP column to first index
        cols = list(df.columns)
        cols.insert(1, cols.pop(cols.index('TIMESTAMP'))) # pop and insert TIMESTAMP at index 1
        df = df.loc[:, cols] # rearrange df
        df_meta = df_meta.loc[:, cols]
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

