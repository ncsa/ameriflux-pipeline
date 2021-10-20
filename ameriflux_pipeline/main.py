# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import configparser
import argparse
import utils.data_util as data_util

from preprocessor import Preprocessor
from format import Format

def perform_data_processing(input_met_path, input_precip_path, output_path, meta_data_path, missing_time_threshold):
    """Create processed dataframe

        Args:
            input_met_path (str): A file path for the input meteorological data.
            input_precip_path (str) : file path for input precipitation data
            output_path (str): A file path for the output data. not currently used as output path is just "_eddypro" appended to input filename.
            meta_data_path (str) : file path for meta data file. not currently used as meta data is created from met file
            missing_time_threshold (int): Number of 30min timeslot threshold

        Returns:
            obj: Pandas DataFrame object.

    """
    df, file_meta = Preprocessor.data_preprocess(input_met_path, input_precip_path, output_path, missing_time_threshold, meta_data_path)
    return df, file_meta


def perform_data_formatting(input_data_path, input_soil_key, file_meta, output_path):
    """
    Create dataframe formatted for EddyPro

        Args:
            input_data_path (str): A file path for the input met data.
            input_soil_key (str): A file path for input soil key sheet
            file_meta (obj) : A pandas dataframe containing meta data about the input met data file
            output_path (str): A file path for the output data.

        Returns:
            obj: Pandas DataFrame object.
    """
    df = Format.data_formatting(input_data_path, input_soil_key, file_meta, output_path)
    return df


def main(*args):
    """Main function to run. Calls other functions

    Args: None

    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--inputmet", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_JanMar2021.csv"),
                        help="input met data path")
    parser.add_argument("--inputprecip", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "Precip_IWS_Jan-Feb_2021.xlsx"),
                        help="input precipitation data path")
    parser.add_argument("--inputsoilkey", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "Soils key.xlsx"))
    parser.add_argument("--output", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_JanMar2021_output.csv"),
                        help="output data path")
    #parser.add_argument("--missingTime", action="store", default=96, help="Number of 30min timeslot threshold to ask for user confirmation")
    parser.add_argument("--metadata", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC.dat.meta.csv"),
                        help="meta data file path") # not currently used as this is automated

    # parse arguments
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    missingTime = int(config['MetDataPreprocessor']['missingTime'])

    # start preprocessing data
    df = perform_data_processing(args.inputmet, args.inputprecip, args.output, args.metadata, missingTime)
    # write processed df to output path
    data_util.write_data(df, args.output)

    output_filename = os.path.basename(args.output)
    eddypro_output_filename = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_output_file = os.path.join(os.getcwd(), "tests", "data", eddypro_output_filename)
    # start formatting data
    df = perform_data_formatting(args.output, args.inputsoilkey, eddypro_output_file)
    # write formatted df to output path
    data_util.write_data(df, eddypro_output_file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()