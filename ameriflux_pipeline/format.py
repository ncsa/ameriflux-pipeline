import pandas as pd
import numpy as np
import shutil

import warnings
warnings.filterwarnings("ignore")


class Format:
    '''
    class to implement formatting meteorological data for eddypro as per guide
    '''
    def __init__(self, input_path, output_path):
        """Constructor for the class

            Args:
                input_path (str): A file path for the input data.
                output_path (str): A file path for the output data.

            Returns:
            obj: Pandas DataFrame object.
        """
        self.input_path = input_path  # path of input data csv file
        self.output_path = output_path  # path to write the formatted meteorological data file

    def read_rename(self):
        """
        Copy and rename input data file. Rename the file as output_path. Use this df for further processing
        Args:
            None
        Returns:
            None
        """
        shutil.copyfile(self.input_path, self.output_path)
        self.df = pd.read_csv(self.output_path)

    def timestamp_format(self):
        """
        Function to change TIMESTAMP format. Replace inplace / with -
        Args:
            None
        Returns:
            None
        """
        self.df['TIMESTAMP'] = self.df['TIMESTAMP'].map(lambda t: t.replace('/', '-'))

    def choose_air_temp(self):
        """
        Function to choose air temperature measurements. Either AirTC_Avg or RTD_C_Avg.
        RTD being more accurate measurement, choose RTD_C_Avg for eddypro. If not present, choose AirTC_Avg
        Args:
            None
        Returns:
            str: the chosen column name
        """
        if 'RTD_C_Avg' in self.df.columns:
            return 'RTD_C_Avg'
        elif 'AirTC_Avg' in self.df.columns:
            return 'AirTC_Avg'
        else:
            return ''


    def required_columns(self, chosen_air_temp):
        """
        Gets a dictionary of required columns with its EddyPro label. This dict is as per the guide and the met variables key.
        Change this dict if variables need to be added / deleted.
        Args:
            None
        Returns:
            dict : a dict of required column names as key and eddypro labels as value
        """
        ### TODO : omitted RAIN_ variable for now as data is not yet available
        ### TODO: ask Bethany if SoilTemp0_Avg is the one that's needed for EddyPro label Ts - many SoilTemp(x)_Avg measurements
        ### TODO: ask Bethany if soil heal flux variable is 'shf_Avg(1)' or 'shf_Avg(2)' or shf_cal_Avg (old data)
        ### TODO: ask Bethany if 'Moisture0_Avg' is the one used for SWC
        col_label = {chosen_air_temp:'Ta', 'RH_Avg':'RH', 'TargTempK_Avg':'Tc', 'albedo_Avg':'Rr',
                    'Rn_Avg':'Rn', 'LWDnCo_Avg':'LWin', 'LWUpCo_Avg':'LWout', 'SWDn_Avg':'SWin', 'SWUp_Avg':'SWout',
                     'PARDown_Avg':'PPFD', 'PARUp_Avg':'PPFDr', 'WindSpeed_Avg':'MWS', 'WindDir_Avg':'WD',
                     'SoilTemp0_Avg':'Ts', 'shf_Avg(1)':'SHF', 'Moisture0_Avg' : 'SWC'
                     }
        return col_label


    def convert_temp_unit(self):
        """
        Method to change temperature measurement unit from celsius to kelvin. Convert inplace
        Args:
            None
        Returns:
            None
        """
        temp_cols = ['Ta', 'Tc', 'Ts'] # list of variables to convert units
        ### TODO : adding 273 to -9999 will give an actual number and not 'NAN'. Need to think what can be done
        ### Either perform addition for numerical values only
        self.df[temp_cols] += 273.15



    def convert_numeric(self):
        """
        Method to convert all non-numeric values to -9999.0 inplace. Step 7 in guide.
        Args:
            None
        Returns:
            None
        """
        self.df.replace({'NAN': -9999.0}, inplace=True)


    # main function to run which calls other functions
    def data_formatting(self):
        """Formats and process the dataframe as per the guide
            Process dataframe inplace
            Args: None

            Returns:
                obj: Pandas DataFrame object
        """
        # read data file to dataframe. step 1 of guide
        self.read_rename()

        # step 3 of guide. change timestamp format
        self.timestamp_format()
        # choose air temperature from 2 measurements
        chosen_air_temp = self.choose_air_temp()
        # step 4. get required columns and the corresponding EddyPro labels
        col_label = self.required_columns(chosen_air_temp)
        required_cols = col_label.keys() # get the required cols from met data
        self.df = self.df[required_cols] # df contains variables for eddyPro. this will be used for further processing
        # rename columns to eddypro labels - as per dict col_label
        self.df.rename(columns=col_label, inplace=True)
        # skip step 5 as it will be managed in pyfluxPro

        # all empty values are replaced by 'NAN' in preprocessor.replace_empty() function
        # step 7 in guide. Change all 'NAN' or non-numeric values to -9999.0
        self.convert_numeric()
        # step 6 in guide. convert temperature measurements from celsius to kelvin
        self.convert_temp_unit()

        # return formatted df
        return self.df




