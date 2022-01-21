import numpy as np
import pandas as pd
import shutil
import re

import warnings
warnings.filterwarnings("ignore")


class EddyProFormat:
    '''
    Class to implement formatting meteorological data for EddyPro as per guide
    '''

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_data_path, input_soil_key, file_meta, output_path):
        """
        Formats the master met data for EddyPRo run.

        Args:
            input_data_path (str): A file path for the input met data.
            input_soil_key (str): A file path for input soil key sheet
            file_meta (obj) : A pandas dataframe containing meta data about the input met data file
            output_path (str): A file path for the output data.
        Returns:
            obj: Pandas DataFrame object.
        """
        input_path = input_data_path  # path of input data csv file
        input_soil_key = input_soil_key  # path for soil key
        file_meta = file_meta  # df containing meta data of file
        output_path = output_path  # path to write the formatted meteorological data file

        # extract site name from file meta data
        # NOTE 3
        file_site_name = file_meta.iloc[0][5]
        # match file site name to site names in soil key file. this is used as lookup in soil key table
        site_name = EddyProFormat.get_site_name(file_site_name)

        # read soil key file
        df_soil_key = EddyProFormat.read_soil_key(input_soil_key)
        # get the soil temp and moisture keys for the site
        eddypro_soil_moisture_labels, eddypro_soil_temp_labels = EddyProFormat.get_soil_keys(df_soil_key, site_name)

        # read data file to dataframe. step 1 of guide
        df = EddyProFormat.read_rename(input_path, output_path)

        # all empty values are replaced by 'NAN' in preprocessor.replace_empty() function
        # replace 'NAN' with np.nan for ease of manipulation
        # TODO : check if this conversion is needed. Currently it is used in fillna function
        df.replace('NAN', np.nan, inplace=True)

        # step 3 of guide. change timestamp format
        df = EddyProFormat.timestamp_format(df)  # / to -

        # rename air temp column names
        eddypro_air_temp_labels = EddyProFormat.air_temp_colnames(df)
        # rename shf measurement
        eddypro_shf_labels = EddyProFormat.shf_colnames(df)
        # rename met variables to eddypro labels
        eddypro_col_labels = {'TIMESTAMP': 'TIMESTAMP', 'RH_Avg': 'RH', 'TargTempK_Avg': 'Tc', 'albedo_Avg': 'Rr',
                              'Rn_Avg': 'Rn', 'LWDnCo_Avg': 'LWin', 'LWUpCo_Avg': 'LWout', 'SWDn_Avg': 'SWin',
                              'SWUp_Avg': 'SWout', 'PARDown_Avg': 'PPFD', 'PARUp_Avg': 'PPFDr',
                              'Precip_IWS': 'P_rain', 'WindSpeed_Avg': 'MWS', 'WindDir_Avg': 'WD'}

        # merge all eddypro label dictionaries
        eddypro_labels = EddyProFormat.merge_dicts(eddypro_col_labels, eddypro_air_temp_labels, eddypro_shf_labels,
                                                   eddypro_soil_temp_labels, eddypro_soil_moisture_labels)

        df.rename(columns=eddypro_labels, inplace=True)

        # skip step 5 as it will be managed in pyfluxPro

        # step 6 in guide. convert temperature measurements from celsius to kelvin
        df = EddyProFormat.convert_temp_unit(df)

        # step 7 in guide. Change all NaN or non-numeric values to -9999.0
        df = EddyProFormat.replace_nonnumeric(df)
        # get units for EddyPro labels
        df = EddyProFormat.replace_units(df)

        # check if required columns from meteorological file are in df
        EddyProFormat.check_req_columns(df)

        # return formatted df
        return df

    @staticmethod
    def get_site_name(file_site_name):
        """
        Match the file site name to site names in soil key data.
        From the input file site name, return the matching site name
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
            eddypro_soil_moisture_labels(dict): Dictionary for soil moisture mapping from met variable to eddypro label
            eddypro_soil_temp_labels(dict): Dictionary for soil temperature mapping from met variable to eddypro label
        """
        site_soil_key = df_soil_key[df_soil_key['Site name'] == site_name]  # get all variables for the site
        # get soil temp and moisture variables
        site_soil_moisture = site_soil_key[['Datalogger/met water variable name',
                                            'EddyPro water variable name']]
        site_soil_temp = site_soil_key[['Datalogger/met temperature variable name',
                                        'EddyPro temperature variable name']]
        col_rename = {'Datalogger/met water variable name': 'Met variable',
                      'Datalogger/met temperature variable name': 'Met variable',
                      'EddyPro water variable name': 'Eddypro label',
                      'EddyPro temperature variable name': 'Eddypro label'
                      }
        site_soil_moisture.rename(columns=col_rename, inplace=True)
        site_soil_temp.rename(columns=col_rename, inplace=True)
        # make these variable labels as dictionary
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
    def read_soil_key(input_soil_key):
        """
        Method to read soil key excel file.
        Soil key file contains the mapping for met variables and eddypro labels for soil temp and moisture
        Returns the df

        Args :
            input_soil_key (str): soil key file path
        Returns :
            obj : pandas dataframe object of the soil keys
        """
        soil_key_df = pd.read_excel(input_soil_key)  # read excel file
        return soil_key_df

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
        df['TIMESTAMP'][0] = 'yyyy-mm-dd HH:MM'  # Change unit TS to yyyy-mm-dd HH:MM to match eddypro format
        return df

    @staticmethod
    def air_temp_colnames(df):
        """
        Function to rename air temperature measurements.
        Rename AirTC_Avg, RTD_C_Avg to Ta_1_1_1 and Ta_1_1_2, where Ta_1_1_1 must be present.
        RTD being more accurate measurement, rename RTD_C_Avg to Ta_1_1_1 for eddypro. If not present, rename AirTC_Avg

        Args:
            df (object): Pandas DataFrame object
        Returns:
            dictionary: met column name and eddypro label mapping
        """
        air_temp_cols = ['RTD_C_Avg', 'AirTC_Avg']
        if set(air_temp_cols).issubset(set(df.columns)):
            return {'RTD_C_Avg': 'Ta_1_1_1', 'AirTC_Avg': 'Ta_1_1_2'}
        elif 'RTD_C_Avg' in df.columns:
            return {'RTD_C_Avg': 'Ta_1_1_1'}
        else:
            return {'AirTC_Avg': 'Ta_1_1_1'}

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
    def convert_temp_unit(df):
        """
        Method to change temperature measurement unit from celsius to kelvin. Convert inplace

        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
        """
        # get all temp variables : get all variables where the unit(2nd row) is 'Deg C' or 'degC'
        temp_cols = [c for c in df.columns if df.iloc[0][c] in ['Deg C', 'degC', 'deg_C']]
        df_temp = df[temp_cols]
        df_temp = df_temp.iloc[1:, :]  # make sure not to reset index here as we need to insert unit row at index 0
        df_temp = df_temp.apply(pd.to_numeric, errors='coerce')  # convert string to numerical
        df_temp += 273.15
        df_temp.loc[0] = ['K'] * df_temp.shape[1]  # add units as Kelvin as row index 0
        df_temp = df_temp.sort_index()  # sorting by index
        df_temp.round(3)
        df.drop(temp_cols, axis=1, inplace=True)
        df = df.join(df_temp)  # join 2 df on index

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
        df.fillna(value=-9999, inplace=True)
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
    def check_req_columns(df):
        """
        Method to check if all required columns are in df. If required list of columns not present, throw a warning

        Args:
            df (object): Pandas DataFrame object
        Returns:
            None
        """
        req_cols = ['SWin', 'RH', 'LWin', 'PPFD']
        if not set(req_cols).issubset(set(df.columns)):
            print("WARNING")
            print(' and '.join(set(req_cols).difference(df.columns)), end='')
            print(" are not present")
        else:
            print("All required columns are present in dataframe")
