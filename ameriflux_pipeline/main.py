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


def preprocessing(input_path, output_path, meta_data_path, missing_time_threshold):
    """Create processed dataframe

        Args:
            input_path (str): A file path for the input data.
            output_path (str): A file path for the output data.
            missing_time_threshold (int): Number of 30min timeslot threshold

        Returns:
            obj: Pandas DataFrame object.

    """
    preprocessor = Preprocessor(input_path, output_path, missing_time_threshold, meta_data_path)
    df = preprocessor.read_data()
    print("Data contains ", df.shape[0], "rows ", df.shape[1], "columns")
    df = preprocessor.data_preprocess()

    return df

def formatting(input_met_data, output_eddypro_data):
    """
    ### TODO: write docstring
    :param input_met_data:
    :param output_eddypro_data:
    :return:
    """
    format = Format(input_met_data, output_eddypro_data)
    df = format.data_formatting()
    return df



def main(*args):
    """Main function to run. Calls other functions

    Args: None

    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--inputMet", action="store", default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC.dat.csv"),
                        help="input meteorological data path")
    parser.add_argument("--outputMet", action="store", default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_output.csv"),
                        help="output meterological data path")
    parser.add_argument("--inputMetaData", action="store", default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC.dat.meta.csv"),
                        help="meta data file path")
    parser.add_argument("--outputEddyPro", action='store',default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC_output_eddypro.csv"),
                        help="output EddyPro data path")

    #parser.add_argument("--missingTime", action="store", default=96, help="Number of 30min timeslot threshold to ask for user confirmation")

    # parse arguments

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    missingTime = int(config['MetDataPreprocessor']['missingTime'])
    # start preprocessing data
    df = preprocessing(args.inputMet, args.outputMet, args.inputMetaData, missingTime)
    # write processed df to output path
    data_util.write_data(df, args.outputMet)

    df_formated = formatting(args.outputMet, args.outputEddyPro)
    # write formatted df to output path
    data_util.write_data(df_formated, args.outputEddyPro)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
