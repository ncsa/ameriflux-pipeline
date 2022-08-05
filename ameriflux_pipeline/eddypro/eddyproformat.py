# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import numpy as np
import pandas as pd
import shutil
import re
import logging

from utils.process_validation import DataValidation
import utils.data_util as data_util

# create log object with current module name
log = logging.getLogger(__name__)


class EddyProFormat:
    """
    Class to implement formatting meteorological data for EddyPro as per guide
    """

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
        site_name = data_util.get_site_name(file_site_name)

        # read soil key file. File contains the mapping for met variables and eddypro labels for soil temp and moisture
        df_soil_key = data_util.read_excel(input_soil_key)
        if not DataValidation.is_valid_soils_key(df_soil_key):
            log.error("Soils_key.xlsx file invalid format. Aborting")
            return None
        # get the soil temp and moisture keys for the site
        eddypro_soil_moisture_labels, eddypro_soil_temp_labels = EddyProFormat.get_soil_keys(df_soil_key, site_name)

        # read data file to dataframe. step 1 of guide
        df = EddyProFormat.read_rename(input_path, output_path)

        # all empty values are replaced by 'NAN' in preprocessor.replace_empty() function
        # replace 'NAN' with np.nan for ease of manipulation
        df.replace('NAN', np.nan, inplace=True)

        # step 3 of guide. change timestamp format
        df = EddyProFormat.timestamp_format(df)  # change / to -

        # rename air temp column names
        eddypro_air_temp_labels = EddyProFormat.air_temp_colnames(df.columns)
        # rename shf measurement
        eddypro_shf_labels = EddyProFormat.shf_colnames(df.columns)
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

        # step 7 in guide. Change all NaN or non-numeric values to -9999
        df = EddyProFormat.replace_nonnumeric(df)
        # get units for EddyPro labels
        df = EddyProFormat.replace_units(df)

        # check if required columns from meteorological file are in df
        EddyProFormat.check_req_columns(df)

        # return formatted df
        return df

    @staticmethod
    def get_soil_keys(df_soil_key, site_name):
        """
        Get mapping from met variable to eddypro soil keys for the specific site.
        Returns dictionary for soil moisture and soil temp variables

        Args:
            df_soil_key (obj): pandas dataframe having soil keys
            site_name (str): site name extracted from file meta data
        Returns:
            eddypro_soil_moisture_labels(dict): Dictionary for soil moisture mapping from met variable to eddypro label
            eddypro_soil_temp_labels(dict): Dictionary for soil temperature mapping from met variable to eddypro label
        """
        site_name_col = df_soil_key.filter(regex=re.compile("^name|^site", re.IGNORECASE)).columns.to_list()[0]
        site_soil_key = df_soil_key[df_soil_key[site_name_col] == site_name]  # get all variables for the site
        # get column names matching datalogger / met tower
        met_cols = site_soil_key.filter(regex=re.compile("datalogger|met tower", re.IGNORECASE)).columns.to_list()
        # get column names matching eddypro
        eddypro_cols = site_soil_key.filter(regex=re.compile("^eddypro", re.IGNORECASE)).columns.to_list()
        # remove variable columns that have 'old' in the name
        old_pattern = re.compile(r'old', re.IGNORECASE)
        met_cols = list(filter(lambda x: not old_pattern.search(x), met_cols))
        eddypro_cols = list(filter(lambda x: not old_pattern.search(x), eddypro_cols))
        # get temp and water variable columns from the above column list
        temp_pattern = re.compile(r'temperature|temp', re.IGNORECASE)
        water_pattern = re.compile(r"water|moisture", re.IGNORECASE)
        met_temp_col = list(filter(temp_pattern.search, met_cols))
        met_water_col = list(filter(water_pattern.search, met_cols))
        eddypro_temp_col = list(filter(temp_pattern.search, eddypro_cols))
        eddypro_water_col = list(filter(water_pattern.search, eddypro_cols))
        # get soil temp and moisture variables
        site_soil_moisture = site_soil_key[[met_water_col[0], eddypro_water_col[0]]]
        site_soil_temp = site_soil_key[[met_temp_col[0], eddypro_temp_col[0]]]
        col_rename = {met_water_col[0]: 'Met variable', met_temp_col[0]: 'Met variable',
                      eddypro_water_col[0]: 'Eddypro label', eddypro_temp_col[0]: 'Eddypro label'}
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
        df = data_util.read_csv_file(output_path, dtype='unicode')
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
        df = df.astype({'TIMESTAMP': str})
        df['TIMESTAMP'] = df['TIMESTAMP'].map(lambda t: t.replace('/', '-'))
        df['TIMESTAMP'][0] = 'yyyy-mm-dd HH:MM'  # Change unit TS to yyyy-mm-dd HH:MM to match eddypro format
        return df

    @staticmethod
    def air_temp_colnames(df_cols):
        """
        Function to rename air temperature measurements.
        Rename AirTC_Avg, RTD_C_Avg to Ta_1_1_1 and Ta_1_1_2, where Ta_1_1_1 must be present.
        RTD being more accurate measurement, rename RTD_C_Avg to Ta_1_1_1 for eddypro. If not present, rename AirTC_Avg

        Args:
            df_cols (object): Pandas DataFrame object columns
        Returns:
            dictionary: met column name and eddypro label mapping
        """
        df_cols = [col.lower() for col in df_cols]
        rtd_pattern = re.compile('^rtd_?c?_?avg')
        airtc_pattern = re.compile('^air_?tc_?avg')
        rtd_col = list(filter(rtd_pattern.match, df_cols))
        airtc_col = list(filter(airtc_pattern.match, df_cols))
        air_temp_cols = None
        if rtd_col and airtc_col:
            air_temp_cols = [rtd_col[0], airtc_col[0]]
        if air_temp_cols and (set(air_temp_cols).issubset(set(df_cols))):
            return {rtd_col[0]: 'Ta_1_1_1', airtc_col[0]: 'Ta_1_1_2'}
        elif rtd_col and rtd_col[0] in df_cols:
            return {rtd_col[0]: 'Ta_1_1_1'}
        elif airtc_col and airtc_col[0] in df_cols:
            return {airtc_col[0]: 'Ta_1_1_1'}
        else:
            return {}

    @staticmethod
    def shf_colnames(df_cols):
        """
        Function to rename soil heat flux measurements. shf_Avg(1), shf_Avg(2) to be renamed as SHF_1_1_1 and SHF_2_1_1.

        Args:
            df_cols (object): Pandas DataFrame object columns
        Returns:
            dictionary: mapping from met variable to eddypro label
        """
        df_cols = [col.lower() for col in df_cols]
        shf1_pattern = re.compile('shf_avg\\(1\\)|shf_avg1|shf_avg_1|shfavg\\(1\\)|shfavg_1')
        shf2_pattern = re.compile('shf_avg\\(2\\)|shf_avg2|shf_avg_2|shfavg\\(2\\)|shfavg_2')
        shf1_col = list(filter(shf1_pattern.match, df_cols))
        shf2_col = list(filter(shf2_pattern.match, df_cols))
        shf_cols = None
        if shf1_col and shf2_col:
            shf_cols = [shf1_col[0], shf2_col[0]]
        if shf_cols and (set(shf_cols).issubset(set(df_cols))):
            return {shf1_col[0]: 'SHF_1_1_1', shf2_col[0]: 'SHF_2_1_1'}
        elif shf1_col and [0] in df_cols:
            return {shf1_col[0]: 'SHF_1_1_1'}
        elif shf2_col and shf2_col[0] in df_cols:
            return {shf2_col[0]: 'SHF_2_1_1'}
        else:
            return {}

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
        temp_cols = [c for c in df.columns if str(df.iloc[0][c]).lower() in ['deg c', 'degc', 'deg_c']]
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
        Method to convert all NaNs to -9999 inplace. Step 7 in guide.

        Args:
            df (object): Pandas DataFrame object
        Returns:
            df (object): Processed Pandas DataFrame object
        """
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
        df.replace({'(?i)W/m^2': 'W+1m-2', '√Ç¬µmols/m√Ç¬≤/s': 'umol+1m-2s-1', '¬µmols/m¬≤/s': 'umol+1m-2s-1',
                    '(?i)Kelvin': 'K', 'm/s': 'm+1s-1', '(?i)Deg': 'degrees', '(?i)vwc': 'm+3m-3'},
                   regex=True, inplace=True)  # replace units using regex. (?i) is for case-insensitive
        # replace the text which has word µmols/m
        df = df.replace(to_replace=r".*mols/m.*", value='umol+1m-2s-1', regex=True)
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
        df_cols = df.columns.to_list()
        # convert to lowercase for comparison
        req_cols = [col.lower() for col in req_cols]
        df_cols = [col.lower() for col in df_cols]
        if not set(req_cols).issubset(set(df_cols)):
            log.warning("Columns are not present in met_output_eddypro"
                        .format(' and '.join(set(req_cols).difference(df_cols))))
        else:
            log.info("All required columns are present in met_output_eddypro")
