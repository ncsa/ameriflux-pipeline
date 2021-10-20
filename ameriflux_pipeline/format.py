import numpy as np
import pandas as pd
import shutil
import re
import utils.data_util as data_util

import warnings
warnings.filterwarnings("ignore")


class Format:
    '''
    class to implement formatting meteorological data for eddypro as per guide
    '''

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_data_path, input_soil_key, file_meta, output_path):
        """Constructor for the class

            Args:
                input_data_path (str): A file path for the input data.
                input_soil_key (str): A file path for input soil key sheet
                file_meta (obj) : A pandas dataframe containing meta data about the input met data file
                output_path (str): A file path for the output data.

            Returns:
            obj: Pandas DataFrame object.
        """
        input_path = input_data_path  # path of input data csv file
        input_soil_key = input_soil_key # path for soil key
        file_meta = file_meta # df containing meta data of file
        output_path = output_path  # path to write the formatted meteorological data file

        # extract site name from file meta data
        file_site_name = file_meta.iloc[0][5]
        # read data file to dataframe. step 1 of guide
        df = Format.read_rename(input_path, output_path)

        # drop the first row having units. done to make df easier to manipulate. units will be added as the end.
        df = df.iloc[1:,:]

        # all empty values are replaced by 'NAN' in preprocessor.replace_empty() function
        # replace 'NAN' with np.nan for ease of manipulation
        ### TODO : check if this conversion is needed.
        df.replace('NAN', np.nan)

        # step 3 of guide. change timestamp format
        df = Format.timestamp_format(df)  # / to -

        # read soil key file
        df_soil_key = Format.read_soil_key(input_soil_key)

        # rename air temp column names
        air_temp_colnames = Format.air_temp_colnames(df)

        # choose shf measurement
        shf_colnames = Format.shf_colnames(df)
        chosen_tc = Format.choose_soil_temp(df) # choose soil temp measurement
        # TODO : update all dictionary column renames air_temp_colnames, shf_colnames,
        # step 4. get required columns and the corresponding EddyPro labels
        col_label = Format.required_columns(chosen_air_temp, chosen_shf, chosen_tc)
        required_cols = col_label.keys()  # get the required cols from met data
        df = df[required_cols]  # df contains variables for eddyPro. this will be used for further processing
        # rename columns to eddypro labels - as per dict col_label
        df.rename(columns=col_label, inplace=True)

        # skip step 5 as it will be managed in pyfluxPro

        # step 6 in guide. convert temperature measurements from celsius to kelvin
        Format.convert_temp_unit(df)

        # step 7 in guide. Change all NaN or non-numeric values to -9999.0
        Format.convert_numeric(df)
        # get units for labels as first row
        df = Format.add_units(df)
        # check if required columns are in df
        ### TODO : check with Bethany variable name for air pressure
        req_cols = ['Ta', 'air_pressure', 'RH_Avg','SWin', 'LWin', 'PPFDr'] # list of required columns

        ### TODO : create a function to check for required columns
        #if not Format.check_columns(df, req_cols):
            #print("ERROR in dataframe")

        # return formatted df
        return df


    @staticmethod
    def read_rename(input_path, output_path):
        """
        Copy and rename input data file. Rename the file as output_path. Use this df for further processing. Return df
        Args:
            input_path (str): A file path for the input data.
            output_path (str): A file path for the output data.
        Returns:
            df(obj): Pandas DataFrame object
        """
        shutil.copyfile(input_path, output_path)
        df = pd.read_csv(output_path)
        return df


    @staticmethod
    def timestamp_format(df):
        """
        Function to change TIMESTAMP format in df. Replace inplace / with -
        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Pandas DataFrame object
        """
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.replace('/', '-'))
        return df

    @staticmethod
    def read_soil_key(input_soil_key):
        """
        Method to read soil key excel file. Soil key file contains the mapping for met variables and eddypro labels for soil temp and moisture
        Returns the df
            Args :
                input_soil_key (str): soil key file path
            Returns :
                obj : pandas dataframe object of the soil keys
        """
        soil_key_df = pd.read_excel(input_soil_key)  # read excel file
        return soil_key_df

    @staticmethod
    def air_temp_colnames(df):
        """
        Function to rename air temperature measurements. Rename AirTC_Avg, RTD_C_Avg to Ta_1_1_1 and Ta_1_1_2, where Ta_1_1_1 must be present.
        RTD being more accurate measurement, rename RTD_C_Avg to Ta_1_1_1 for eddypro. If not present, rename AirTC_Avg
        Args:
            df (object): Pandas DataFrame object
        Returns:
            dictionary: met column name and eddypro label mapping
        """
        air_temp_cols = ['RTD_C_Avg', 'AirTC_Avg' ]
        if set(air_temp_cols).issubset(set(df.columns)):
            return {'RTD_C_Avg':'Ta_1_1_1', 'AirTC_Avg':'Ta_1_1_2'}
        elif 'RTD_C_Avg' in df.columns:
            return {'RTD_C_Avg':'Ta_1_1_1'}
        else:
            return {'AirTC_Avg':'Ta_1_1_1'}


    @staticmethod
    def shf_colnames(df):
        """
        Function to rename soil heat flux measurements. shf_Avg(1), shf_Avg(2) to be renamed as SHF_1_1_1 and SHF_2_1_1.
        Args:
            df (object): Pandas DataFrame object
        Returns:
            dictionary: mapping from met variable to eddypro label
        """
        shf_cols = ['shf_Avg(1)', 'shf_Avg(2)']
        if set(shf_cols).issubset(set(df.columns)):
            return {'shf_Avg(1)': 'SHF_1_1_1', 'shf_Avg(2)': 'SHF_2_1_1'}
        elif 'shf_Avg(1)' in df.columns:
            return {'shf_Avg(1)': 'SHF_1_1_1'}
        else:
            return {'shf_Avg(2)': 'SHF_2_1_1'}


    @staticmethod
    def soil_temp_colnames(df):
        """
        Function to rename soil temp measurements.
        Either TC_10cm_Avg, TC1_10cm_Avg or TC2_10cm_Avg - use regex to match. If multiple fields present, choose the one with least missing values.
        Args:
            df (object): Pandas DataFrame object
        Returns:
            str: the chosen column name
        """
        column_string = ' '.join(df.columns)
        pattern = 'TC\d*_10cm_Avg'
        match = re.findall(pattern, column_string)
        if len(match)==1:
            return match[0]
        else:
            # multiple field names match. choose one with min NAN
            col_numNAN={}
            for col in match:
                col_numNAN[col]=len(df[df[col]=='NAN'])
            # return col name with minimum value
            return min(col_numNAN, key=col_numNAN.get)


    @staticmethod
    def required_columns(chosen_air_temp, chosen_shf, chosen_tc):
        """
        Create a dictionary of required columns with its EddyPro label. This dict is as per the guide and the met variables key.
        Change this dict if variables need to be added / deleted.
        Args:
            chosen_air_temp (string) : air temp column name
            chosen_shf (string) : soil heat flux column name
            chosen_tc (string) : soil temp column name
        Returns:
            dict : a dict of required column names as key and eddypro labels as value
        """
        ### TODO: Soil Temp - confirm with Bethany if the method is right. Currently using TC_10cm_Avg field - many SoilTemp(x)_Avg measurements

        ### TODO: check with Bethany if 'Moisture0_Avg' is the one used for SWC - pending. Bethany working on table to match keys.
        # depends on field / filename

        ### TODO: check with Bethany WindSpeed_Avg and WindDir_Avg - what to do if timestamp != 2000. what to do for other timestamps
        # 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD' - needed for older than 2020.
        # if yyyy==2000, do not use 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD'
        col_label = { 'TIMESTAMP':'TIMESTAMP', chosen_air_temp:'Ta', 'RH_Avg':'RH', 'TargTempK_Avg':'Tc', 'albedo_Avg':'Rr',
                    'Rn_Avg':'Rn', 'LWDnCo_Avg':'LWin', 'LWUpCo_Avg':'LWout', 'SWDn_Avg':'SWin', 'SWUp_Avg':'SWout',
                    'PARDown_Avg':'PPFD', 'PARUp_Avg':'PPFDr', 'Precip_IWS': 'P_rain', 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD',
                    chosen_tc:'Ts', chosen_shf:'SHF', 'Moisture0_Avg':'SWC'}
        # step 5 in guide
        # TODO : check with Bethany on dynamic naming of met tower variable duplicates. _1_2_1.
        return col_label


    @staticmethod
    def add_units(df):
        """
            Create a dictionary of required labels with its units. This dict is as per the guide and the met variables key.
            Change this dict if variables need to be added / deleted.
            Update the first row of dataframe with new units and return the processed df
            Args:
                df (object): Pandas DataFrame object
            Returns:
                df (object): Processed Pandas DataFrame object
        """
        label_unit_row = pd.DataFrame({'TIMESTAMP': ['TIMESTAMP'], 'Ta': ['K'], 'RH': ['%'], 'Tc': ['K'],
                      'Rr': ['W+1m-2'], 'Rn': ['W+1m-2'], 'LWin': ['W+1m-2'], 'LWout': ['W+1m-2'],
                      'SWin': ['W+1m-2'], 'SWout': ['W+1m-2'],
                      'PPFD': ['umol+1m-2s-1'], 'PPFDr': ['umol+1m-2s-1'], 'P_rain' :['m'],
                      'MWS': ['m+1m-1'], 'WD': ['degrees'], 'Ts': ['K'], 'SHF': ['W+1m-2'], 'SWC': ['m+3m-3']})
        df = pd.concat([label_unit_row,df]).reset_index(drop=True)
        return df


    @staticmethod
    def convert_temp_unit(df):
        """
        Method to change temperature measurement unit from celsius to kelvin. Convert inplace
        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
        """
        #temp_cols = ['Ta', 'Tc', 'Ts'] # list of variables to convert units
        ### TODO : if there is a zero value for Ta, Tc or Ts, the kelvin measurement will read 273.15K instead of 0. Check if change the calculation to ((celsius * 9/5) + 32 ) )
        df['cel_to_K'] = 273.15
        df['Ta'] = df[['Ta', 'cel_to_K']].sum(axis=1) # sum will skip NaNs
        df['Tc'] = df[['Tc', 'cel_to_K']].sum(axis=1)
        df['Ts'] = df[['Ts', 'cel_to_K']].sum(axis=1)
        df.drop('cel_to_K', axis=1, inplace=True)
        return df


    @staticmethod
    def convert_numeric(df):
        """
        Method to convert all NaNs to -9999.0 inplace. Step 7 in guide.
        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
        """
        df.fillna(value=-9999.0, inplace=True)
        return df


    @staticmethod
    def check_columns(df, req_cols):
        """
        Method to check if all required columns are in df
        Args:
            df (object): Pandas DataFrame object
        Returns:
            True / False (bool) : True if all required columns are present. False if not.
        """
        if not set(req_cols).issubset(set(df.columns)):
            print("{' and '.join(set(req_cols).difference(df.columns))} are not present")
            return False
        print( "All required columns are present in dataframe" )
        return True




