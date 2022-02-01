import pandas as pd
import numpy as np
import math
from datetime import timedelta

import warnings
warnings.filterwarnings("ignore")


class AmeriFluxFormat:
    """
    Class to implement formatting of PyFluxPro input excel sheet as per guide
    """

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_file):
        """
        Constructor for the class

        Args:
            input_file (str): A file path for the input data. This is the PyFluxPro input excel sheet
        Returns:
            obj: Pandas DataFrame object.
        """
        full_output_df = pd.read_excel(input_file, sheet_name='full_output')
        met_df = pd.read_excel(input_file, sheet_name='Met_data_30')
        full_output_df_meta = AmeriFluxFormat.get_meta_data(full_output_df)
        met_df_meta = AmeriFluxFormat.get_meta_data(met_df)

        # remove meta data from dataframe
        full_output_df = full_output_df.iloc[1:, :]
        met_df = met_df.iloc[1:, :]
        # Step 1 of guide
        full_output_df = AmeriFluxFormat.replace_empty(full_output_df)
        met_df = AmeriFluxFormat.replace_empty(met_df)
        # step 2 in guide
        met_df = AmeriFluxFormat.timestamp_met_df(met_df)

        return full_output_df, met_df

    @staticmethod
    # get the units column as a meta df
    def get_meta_data(df):
        df_meta = df.head(1)
        return df_meta

    @staticmethod
    def replace_empty(df):
        """
        Function to replace empty and NaN cells

        Args:
            df (object): Pandas DataFrame object
        Returns :
            obj: Pandas DataFrame object
        """
        df = df.replace('', np.nan)  # replace empty cells with 'NAN'
        df = df.replace('NAN', np.nan)
        return df

    @staticmethod
    def timestamp_met_df(df):
        """
        Function to format timestamp in met_data_30

        Args:
            df (object): Pandas DataFrame object
        Returns :
            obj: Pandas DataFrame object
        """
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        # shift each timestamp 30min behind and store in another column
        # df['TIMESTAMP_START'] = df['TIMESTAMP']
        # df['TIMESTAMP_END'] = df['TIMESTAMP'] + timedelta(minutes=30)
        df.insert(0, 'TIMESTAMP_START', df['TIMESTAMP'])
        df.insert(1, 'TIMESTAMP_END', df['TIMESTAMP'] + timedelta(minutes=30))
        return df

    @staticmethod
    def var_unit_changes(full_output_df, full_output_df_meta, met_df, met_df_meta):
        """
        Function to change units of selected variables from full_output and met_data_30

        Args:
            full_output_df (object): Full output of EddyPro dataframe. full_output sheet in pyfluxpro input
            full_output_df_meta (object): Meta data of full output. Contains col names and units
            met_df (object): Met_data_30 sheet of pyfluxpro
            met_df_meta (object): Meta data of met data. Contains col names and units
        Returns :
            obj: Pandas DataFrame object
        """
        # convert columns given in AmeriFlux mainstem keys
        if 'Albedo_Avg' in met_df:
            if met_df['Albedo_Avg'] > 1:
                met_df['ALB'] = 1
            else:
                met_df['ALB'] = 100 * met_df['Albedo_Avg']
            met_df_meta['ALB'] = '[%]'

        if 'VPD' in full_output_df:
            full_output_df['VPD'] = full_output_df['VPD'] / 100
            full_output_df_meta['VPD'].iloc[0] = '[hPa]'
        if 'Tau' in full_output_df:
            full_output_df['Tau'] = full_output_df['Tau'].abs()
            full_output_df_meta['Tau'].iloc[0] = 'kg/m/s^2'
        elif 'co2_sd' in full_output_df:
            full_output_df['CO2_SIGMA'] = math.sqrt(full_output_df['co2_sd'])
            full_output_df_meta['CO2_SIGMA'].iloc[0] = 'umol/mol'
        elif 'h2o_sd' in full_output_df:
            full_output_df['H2O_SIGMA'] = math.sqrt(full_output_df['h2o_sd'])
            full_output_df_meta['H2O_SIGMA'].iloc[0] = 'umol/mol'
        elif 'u_sd' in full_output_df:
            full_output_df['U_SIGMA'] = math.sqrt(full_output_df['u_sd'])
            full_output_df_meta['U_SIGMA'].iloc[0] = 'm/s'
        elif 'v_sd' in full_output_df:
            full_output_df['V_SIGMA'] = math.sqrt(full_output_df['v_sd'])
            full_output_df_meta['V_SIGMA'].iloc[0] = 'm/s'
        elif 'w_sd' in full_output_df:
            full_output_df['W_SIGMA'] = math.sqrt(full_output_df['w_sd'])
            full_output_df_meta['W_SIGMA'].iloc[0] = 'm/s'

        # convert soil moisture variables into percentage values
        soil_moisture_col = [col for col in met_df if col.startswith('Moisture')]
        soil_moisture_col.extend(col for col in met_df if col.startswith('VWC'))
        for col in soil_moisture_col:
            met_df[col] = met_df[col] * 100
            met_df_meta[col].iloc[0] = '[%]'

        return full_output_df, full_output_df_meta, met_df, met_df_meta


