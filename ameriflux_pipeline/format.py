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
        # match file site name to site names in soil key file. this is used as lookup in soil key table
        site_name = Format.get_site_name(file_site_name)

        # read soil key file
        df_soil_key = Format.read_soil_key(input_soil_key)
        # get the soil temp and moisture keys for the site
        eddypro_soil_moisture_labels, eddypro_soil_temp_labels = Format.get_soil_keys(df_soil_key, site_name)

        # read data file to dataframe. step 1 of guide
        df = Format.read_rename(input_path, output_path)

        # drop the first row having units. done to make df easier to manipulate. units will be added as the end.
        #df = df.iloc[1:,:] # not currently used

        # all empty values are replaced by 'NAN' in preprocessor.replace_empty() function
        # replace 'NAN' with np.nan for ease of manipulation
        ### TODO : check if this conversion is needed. Currently it is used in fillna function
        df.replace('NAN', np.nan, inplace=True)

        # step 3 of guide. change timestamp format
        df = Format.timestamp_format(df)  # / to -

        # rename air temp column names
        eddypro_air_temp_labels = Format.air_temp_colnames(df)
        # rename shf measurement
        eddypro_shf_labels = Format.shf_colnames(df)
        # rename met variables to eddypro labels
        eddypro_col_labels = {'TIMESTAMP': 'TIMESTAMP', 'RH_Avg': 'RH', 'TargTempK_Avg': 'Tc', 'albedo_Avg': 'Rr',
                     'Rn_Avg': 'Rn', 'LWDnCo_Avg': 'LWin', 'LWUpCo_Avg': 'LWout', 'SWDn_Avg': 'SWin', 'SWUp_Avg': 'SWout',
                     'PARDown_Avg': 'PPFD', 'PARUp_Avg': 'PPFDr', 'Precip_IWS': 'P_rain', 'WindSpeed_Avg': 'MWS', 'WindDir_Avg': 'WD'}
        # merge all eddypro label dictionaries
        eddypro_labels = Format.merge_dicts(eddypro_col_labels, eddypro_air_temp_labels, eddypro_shf_labels,
                                     eddypro_soil_temp_labels, eddypro_soil_moisture_labels)

        df.rename(columns=eddypro_labels, inplace=True)

        # skip step 5 as it will be managed in pyfluxPro

        # step 6 in guide. convert temperature measurements from celsius to kelvin
        df = Format.convert_temp_unit(df)

        # step 7 in guide. Change all NaN or non-numeric values to -9999.0
        df = Format.replace_nonnumeric(df)
        # get units for EddyPro labels
        df = Format.replace_units(df)

        # check if required columns are in df
        ### TODO : Delete air pressure variables. Air pressure is from ghg file. create a function to check for required columns
        ### TODO : create a function to throw a warning if WindSpeed and WindDir is present for 2021 timeframe
        # req_cols = ['Ta', 'air_pressure', 'RH_Avg','SWin', 'LWin', 'PPFDr'] # list of required columns
        #if not Format.check_columns(df, req_cols):
            #print("ERROR in dataframe")

        # return formatted df
        return df


    @staticmethod
    def get_site_name(file_site_name):
        """
        Match the file site name to site names in soil key data. From the input file site name, return the matching site name
        Site name is used as lookup in soil key table
        Args:
            file_site_name (str): file site name from file meta data, first row of input met file
        Returns:
            (str): matching site name
        """
        if re.match('^CPU:Maize_Control_*', file_site_name):
            return 'Maize-Control'
        elif re.match('^CPU:Maize_*', file_site_name):
            return 'Maize-Basalt'
        elif re.match('^CPU:Miscanthus_Control_*', file_site_name):
            return 'Miscanthus-Control'
        elif re.match('^CPU:Miscanthus_*', file_site_name):
            return 'Miscanthus-Basalt'
        elif re.match('^CPU:Sorghum_*', file_site_name):
            return 'Sorghum'


    @staticmethod
    def get_soil_keys(df_soil_key, site_name):
        """
        Get soil keys for the specific site. Returns dictionary for soil moisture and soil temp variables
        Args:
            df_soil_key (obj): pandas dataframe having soil keys
            site_name (str): site name extracted from file meta data
        Returns:
            eddypro_soil_moisture_labels (dict): Dictionary giving soil moisture mapping from met tower variables to eddypro labels
            eddypro_soil_temp_labels (dict): Dictionary giving soil temperature mapping from met tower variables to eddypro labels
        """
        site_soil_key = df_soil_key[df_soil_key['Site name'] == site_name]
        # get soil temp and moisture
        site_soil_moisture = site_soil_key[['Datalogger/met water variable name', 'EddyPro water variable name']]
        site_soil_temp = site_soil_key[['Datalogger/met temperature variable name', 'EddyPro temperature variable name']]
        col_rename = {'Datalogger/met water variable name': 'Met variable',
                      'Datalogger/met temperature variable name': 'Met variable',
                      'EddyPro water variable name': 'Eddypro label',
                      'EddyPro temperature variable name': 'Eddypro label'
                      }
        site_soil_moisture.rename(columns=col_rename, inplace=True)
        site_soil_temp.rename(columns=col_rename, inplace=True)
        eddypro_soil_moisture_labels = site_soil_moisture.set_index('Met variable').T.to_dict('list')
        eddypro_soil_temp_labels = site_soil_temp.set_index('Met variable').T.to_dict('list')
        # remove list from values
        for key, value in eddypro_soil_moisture_labels.items():
            eddypro_soil_moisture_labels[key] = ''.join(value)
        for key, value in eddypro_soil_temp_labels.items():
            eddypro_soil_temp_labels[key] = ''.join(value)
        return eddypro_soil_moisture_labels, eddypro_soil_temp_labels


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
        df['TIMESTAMP'][0] = 'yyyy-mm-dd HH:MM'
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
    def merge_dicts(*dict_args):
        """
        Function to merge all eddypro label dictionaries. Return the merged dict
        Given any number of dictionaries, shallow copy and merge into a new dict,
        precedence goes to key-value pairs in latter dictionaries.
        Args:
            dict_args (python args) : any number of dictionaries
        Returns:
            dictionary: mapping from met variable to eddypro label
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result


    @staticmethod
    def soil_temp_colnames(df):
        """
        Not used currently
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
        Not used currently
        Create a dictionary of required columns with its EddyPro label. This dict is as per the guide and the met variables key.
        Change this dict if variables need to be added / deleted.
        Args:
            chosen_air_temp (string) : air temp column name
            chosen_shf (string) : soil heat flux column name
            chosen_tc (string) : soil temp column name
        Returns:
            dict : a dict of required column names as key and eddypro labels as value
        """
        # 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD' - needed for older than 2020.
        # if yyyy==2000, do not use 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD'
        col_label = { 'TIMESTAMP':'TIMESTAMP', chosen_air_temp:'Ta', 'RH_Avg':'RH', 'TargTempK_Avg':'Tc', 'albedo_Avg':'Rr',
                    'Rn_Avg':'Rn', 'LWDnCo_Avg':'LWin', 'LWUpCo_Avg':'LWout', 'SWDn_Avg':'SWin', 'SWUp_Avg':'SWout',
                    'PARDown_Avg':'PPFD', 'PARUp_Avg':'PPFDr', 'Precip_IWS': 'P_rain', 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD',
                    chosen_tc:'Ts', chosen_shf:'SHF', 'Moisture0_Avg':'SWC'}
        return col_label


    @staticmethod
    def convert_temp_unit(df):
        """
        Method to change temperature measurement unit from celsius to kelvin. Convert inplace
        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
        """
        temp_cols = [c for c in df.columns if df.iloc[0][c] in ['Deg C', 'degC', 'deg_C']] # get all temp variables : get all variables where the unit(2nd row) is 'Deg C' or 'degC'
        df_temp = df[temp_cols]
        df_temp = df_temp.iloc[1:, :]  # make sure not to reset index here as we need to insert unit row at index 0
        df_temp = df_temp.apply(pd.to_numeric, errors='coerce') # convert string to numerical
        df_temp += 273.15
        df_temp.loc[0] = ['K'] * df_temp.shape[1] # add units as Kelvin as row index 0
        df_temp = df_temp.sort_index()  # sorting by index
        df_temp.round(3)
        df.drop(temp_cols, axis=1, inplace=True)
        df = df.join(df_temp) # join 2 df on index

        return df


    @staticmethod
    def replace_nonnumeric(df):
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
    def replace_units(df):
        """
            Replace met tower variable units to Eddypro label units
            Args:
                df (object): Pandas DataFrame object
            Returns:
                df (object): Processed Pandas DataFrame object
        """
        df.replace({'W/m^2': 'W+1m-2', '√Ç¬µmols/m√Ç¬≤/s': 'umol+1m-2s-1', 'Kelvin': 'K',
                    'm/s': 'm+1s-1', 'Deg': 'degrees', 'vwc': 'm+3m-3'}, inplace=True)
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




