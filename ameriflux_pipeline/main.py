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

def perform_data_processing(input_path, output_path, meta_data_path, missing_time_threshold,):
    """Create processed dataframe

        Args:
            input_path (str): A file path for the input data.
            output_path (str): A file path for the output data.
            missing_time_threshold (int): Number of 30min timeslot threshold

        Returns:
            obj: Pandas DataFrame object.

    """
    df = Preprocessor.data_preprocess(input_path, output_path, missing_time_threshold, meta_data_path)

    return df


def perform_data_formatting(input_path, output_path):
    """
    Create dataframe formatted for EddyPro

        Args:
            input_path (str): A file path for the input data.
            output_path (str): A file path for the output data.

        Returns:
            obj: Pandas DataFrame object.
    """
    df = Format.data_formatting(input_path, output_path)
    return df


def main(*args):
    """Main function to run. Calls other functions

    Args: None

    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_Oct_week34.csv"),
                        help="input data path")
    parser.add_argument("--output", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_Oct_week34_output.csv"),
                        help="output data path")
    #parser.add_argument("--missingTime", action="store", default=96, help="Number of 30min timeslot threshold to ask for user confirmation")
    parser.add_argument("--metadata", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC.dat.meta.csv"),
                        help="meta data file path")

    # parse arguments
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    missingTime = int(config['MetDataPreprocessor']['missingTime'])

    # start preprocessing data
    df = perform_data_processing(args.input, args.output, args.metadata, missingTime)
    # write processed df to output path
    data_util.write_data(df, args.output)

    output_filename = os.path.basename(args.output)
    eddypro_output_filename = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_output_file = os.path.join(os.getcwd(), "tests", "data", eddypro_output_filename)
    # start formatting data
    df = perform_data_formatting(args.output, eddypro_output_file)
    # write formatted df to output path
    data_util.write_data(df, eddypro_output_file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()