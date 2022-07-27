# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import numpy as np
from datetime import timedelta
import logging

# create log object with current module name
log = logging.getLogger(__name__)


class AmeriFluxFormat:
    """
    Class to implement formatting of PyFluxPro input excel sheet as per guide for Ameriflux submission
    """

    # main method which calls other functions
    @staticmethod
    def data_formatting(input_file, full_output_sheet_name, met_data_sheet_name):
        """
        Method to implement data formatting for PyFluxPro input excel sheet. Calls other methods.

        Args:
            input_file (str): A file path for the input data. This is the PyFluxPro input excel sheet
            full_output_sheet_name (str): full_output sheet name
            met_data_sheet_name (str): Met_data_30 sheet name
        Returns:
            obj: Pandas DataFrame object.
        """

        full_output_df = pd.read_excel(input_file, sheet_name=full_output_sheet_name)
        met_df = pd.read_excel(input_file, sheet_name=met_data_sheet_name)

        # get column names and its units
        full_output_df_meta = AmeriFluxFormat.get_meta_data(full_output_df)
        met_df_meta = AmeriFluxFormat.get_meta_data(met_df)

        # remove meta data from dataframe
        full_output_df = full_output_df.iloc[1:, :]
        met_df = met_df.iloc[1:, :]
        full_output_df.reset_index(drop=True, inplace=True)  # reset index after dropping rows
        met_df.reset_index(drop=True, inplace=True)  # reset index after dropping rows

        # convert -9999 and empty cells to NaN. To make numerical conversions easier.
        full_output_df = AmeriFluxFormat.replace_empty(full_output_df)
        met_df = AmeriFluxFormat.replace_empty(met_df)

        # step 3,4,5,6,7 in guide
        full_output_df, full_output_df_meta, met_df, met_df_meta = AmeriFluxFormat.\
            var_unit_changes(full_output_df, full_output_df_meta, met_df, met_df_meta)

        # Step 1 of guide. convert NaNs back
        full_output_df.replace(np.nan, 'NAN', inplace=True)
        met_df.replace(np.nan, 'NAN', inplace=True)

        # concat the meta df and df if number of columns is the same
        if full_output_df_meta.shape[1] == full_output_df.shape[1]:
            full_output_df = pd.concat([full_output_df_meta, full_output_df], ignore_index=True)
        else:
            log.error("Number of columns in Full_output meta data {} not the same as number of columns in data {}".
                      format(full_output_df_meta.shape[1], full_output_df.shape[1]))
            full_output_df = None
        if met_df_meta.shape[1] == met_df.shape[1]:
            met_df = pd.concat([met_df_meta, met_df], ignore_index=True)
        else:
            log.error("Number of columns in Met_data_30 meta data {} not the same as number of columns in data {}".
                      format(met_df_meta.shape[1], met_df.shape[1]))
            met_df = None

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

    # currently not used
    @staticmethod
    def timestamp_met_df(df, df_meta):
        """
        Function to format timestamp in met_data_30

        Args:
            df (object): Pandas DataFrame object
            df_meta (object) : dataframe containng meta data info about df. Pandas DataFrame object
        Returns :
            df (obj): Formatted Pandas DataFrame object
            df_meta (obj): Formatted Pandas DataFrame object
        """
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        # shift each timestamp 30min behind and store in another column
        df.insert(0, 'TIMESTAMP', df.pop('TIMESTAMP'))
        df.insert(1, 'TIMESTAMP_END', df['TIMESTAMP'] + timedelta(minutes=30))
        df.insert(2, 'TIMESTAMP_START', df['TIMESTAMP'])

        # convert to correct format. Not used currently
        # df = AmeriFluxFormat.timestamp_format(df, ['TIMESTAMP', 'TIMESTAMP_START', 'TIMESTAMP_END'])
        # add columns in meta data
        df_meta.insert(1, 'TIMESTAMP_END', 'TS')
        df_meta.insert(2, 'TIMESTAMP_START', 'TS')

        return df, df_meta

    # currently not used
    @staticmethod
    def timestamp_format(df, timestamp_cols):
        """
        Function to convert datetime to string and correct timestamp format

        Args:
            df (object): Pandas DataFrame object
            timestamp_cols : List of timestamp column names to be formatted
        Returns:
            obj: Pandas DataFrame object
        """
        # convert datetime to string, replace - with /
        for col in timestamp_cols:
            df[col] = df[col].map(lambda t: t.strftime('%Y-%m-%d %H:%M')) \
                                .map(lambda t: t.replace('-', '/'))
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
            (obj): full_output_df processed Pandas DataFrame object
            (obj): full_output_df_meta processed Pandas DataFrame object
            (obj): met_df processed Pandas DataFrame object
            (obj): met_df_meta processed Pandas DataFrame object

        """
        # convert columns given in AmeriFlux mainstem keys
        # get Albedo column and convert to ALB
        try:
            albedo_col = met_df.filter(regex="albedo|Albedo|ALBEDO").columns.to_list()[0]
        except IndexError as ex:
            log.warning("Albedo column not present")
            albedo_col = None
        if albedo_col:
            met_df = met_df.astype({albedo_col: float})
            met_df['ALB'] = met_df[albedo_col].apply(lambda x: float(x)*100 if (0 <= float(x) <= 1) else np.nan)
            met_df_meta['ALB'] = '%'
        vpd_col = full_output_df.filter(regex="VPD|vpd|Vpd").columns.to_list()
        if vpd_col:
            full_output_df['VPD'] = full_output_df[vpd_col[0]] / 100
            full_output_df_meta['VPD'].iloc[0] = '[hPa]'
        else:
            log.warning("VPD column not present in full_output")
        tau_col = full_output_df.filter(regex="Tau|tau|TAU").columns.to_list()
        if tau_col:
            full_output_df['Tau'] = full_output_df[tau_col[0]] * -1.0
            full_output_df_meta['Tau'].iloc[0] = '[kg+1m-1s-2]'
        else:
            log.warning("Tau column not present in full_output")
        # convert soil moisture variables into percentage values
        soil_moisture_col = [col for col in met_df if col.lower().startswith('moisture')]
        soil_moisture_col.extend(col for col in met_df if col.startswith('VWC'))
        for col in soil_moisture_col:
            met_df[col] = met_df[col] * 100
            met_df_meta[col].iloc[0] = '%'

        # convert variances to std deviations in full_output
        variance_vars = [col for col in full_output_df if col.lower().endswith('_var')]
        for col in variance_vars:
            col_sd = col.split('_')[0] + '_sd'
            full_output_df[col_sd] = np.sqrt(full_output_df[col].astype(float))
            if full_output_df_meta[col].iloc[0] == '[m+2s-2]':
                full_output_df_meta[col_sd] = '[m+1s-1]'
            elif full_output_df_meta[col].iloc[0] == '[K+2]':
                full_output_df_meta[col_sd] = '[K]'
            else:
                full_output_df_meta[col_sd] = ''

        return full_output_df, full_output_df_meta, met_df, met_df_meta
