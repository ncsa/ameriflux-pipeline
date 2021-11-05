# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
from config import Config as cfg
import argparse
import utils.data_util as data_util

from preprocessor import Preprocessor
from eddyproformat import EddyProFormat
from pyfluxpro_format import PyFluxProFormat



def perform_data_processing(input_met_path, input_precip_path, missing_time_threshold):
    """Create processed dataframe

    Args:
        input_met_path (str): A file path for the input meteorological data.
        input_precip_path (str) : file path for input precipitation data
        missing_time_threshold (int): Number of 30min timeslot threshold
    Returns:
        obj: Pandas DataFrame object.

    """
    df, file_meta = Preprocessor.data_preprocess(input_met_path, input_precip_path, missing_time_threshold)
    ### TODO : check with Bethany - number of decimal places for numerical values
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
    df = EddyProFormat.data_formatting(input_data_path, input_soil_key, file_meta, output_path)
    return df


def perform_pyfluxpro_processing(met_data, full_output):
    """
    Create dataframe formatted for PyFluxPro

    Args:
        met_data (str): A file path for the master met data created in Preprocessor.
        full_output (str): EddyPro full_output file path
    Returns:
        obj: Pandas DataFrame object.
    """
    df = PyFluxProFormat.data_formatting(full_output)
    # met_data has data from row index 1. EddyPro full_output will be formatted to have data from row index 1 also. This is step 3a in guide.
    # join met_data and full_output in excel sheet (manual step)

    # return formatted full_output
    return df


def get_args():
    """
    Function to get all arguments needed to run main files
    Args: None
    """
    ### TODO : create a dynamic method to pass input files, shouldn't depend on the relative file path
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

    # parse arguments
    args = parser.parse_args()
    missingTime = int(cfg.missingTime)
    full_output = cfg.full_output

    return args.inputmet, args.inputprecip, args.inputsoilkey, missingTime, args.output, full_output


def eddypro_main(inputmet, inputprecip, inputsoilkey, missingTime, output):
    """
    Main function to run EddyPro processing. Calls other functions

    Args: None
    Returns : None
    """
    # start preprocessing data
    df, file_meta = perform_data_processing(inputmet, inputprecip, missingTime)
    # write processed df to output path
    data_util.write_data(df, output)

    output_filename = os.path.basename(output)
    eddypro_output_filename = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_output_file = os.path.join(os.getcwd(), "tests", "data", eddypro_output_filename)
    # start formatting data
    df = perform_data_formatting(output, inputsoilkey, file_meta, eddypro_output_file)
    # write formatted df to output path
    data_util.write_data(df, eddypro_output_file)


def pyfluxpro_main(met_output_file, eddypro_full_output):
    """
    Main function to run PlyFluxPro processing. Calls other functions

    Args: None
    Returns : None
    """
    df = perform_pyfluxpro_processing(met_output_file, eddypro_full_output)
    # write formatted df to output path
    #data_util.write_data(df, pyfluxpro_output_file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    inputmet, inputprecip, inputsoilkey, missingTime, met_output_file, eddypro_full_output = get_args()
    eddypro_main(inputmet, inputprecip, inputsoilkey, missingTime, met_output_file)
    ### TODO : Run EddyPro headless here
    pyfluxpro_main(met_output_file, eddypro_full_output)