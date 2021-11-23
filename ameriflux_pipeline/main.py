# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import shutil
from config import Config as cfg
import argparse
import utils.data_util as data_util

from preprocessor import Preprocessor
from eddyproformat import EddyProFormat
from pyfluxpro_format import PyFluxProFormat


def get_args():
    """
    Function to get all arguments needed to run main files

    Args: None
    Returns : None
    """
    # TODO : create a dynamic method to pass input files, shouldn't depend on the relative file path
    parser = argparse.ArgumentParser()

    parser.add_argument("--inputMet", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data",
                                             "FLUXSB_EC_JanMar2021.csv"),
                        help="input met data path")
    parser.add_argument("--inputPrecip", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data",
                                             "Precip_IWS_Jan-Feb_2021.xlsx"),
                        help="input precipitation data path")
    parser.add_argument("--missingTime", action="store", default=96,
                        help="Number of 30min missing timeslot threshold for user confirmation")
    parser.add_argument("--inputSoilkey", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data",
                                             "Soils key.xlsx"))
    parser.add_argument("--outputMet", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data",
                                             "FLUXSB_EC_JanMar2021_output.csv"),
                        help="output data path")
    parser.add_argument("--fullOutput", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data",
                                             "eddypro_Sorghum_Jan1to7_2021_full_output_2021-11-03T083200_adv.csv"),
                        help="output data path")

    # parse arguments
    args = parser.parse_args()

    return args.inputMet, args.inputPrecip, args.missingTime, args.inputSoilkey, args.outputMet, args.fullOutput


def eddypro_main(input_met, input_precip, input_soilkey, missing_time, output):
    """
    Main function to run EddyPro processing. Calls other functions

    Args:
        input_met (str): A file path for the input meteorological data. For EddyPro processing
        input_precip (str) : file path for input precipitation data. For EddyPro processing
        missing_time (int): Number of 30min timeslot threshold. For EddyPro processing
        input_soilkey (str): A file path for input soil key sheet. For EddyPro formatting
    Returns : None
    """
    # start preprocessing data
    df, file_meta = Preprocessor.data_preprocess(input_met, input_precip, missing_time)
    # TODO : check with Bethany - number of decimal places for numerical values
    # write processed df to output path
    data_util.write_data(df, output)

    output_filename = os.path.basename(output)
    eddypro_output_filename = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_output_file = os.path.join(os.getcwd(), "tests", "data", eddypro_output_filename)
    # start formatting data
    df = EddyProFormat.data_formatting(output, input_soilkey, file_meta, eddypro_output_file)
    # write formatted df to output path
    data_util.write_data(df, eddypro_output_file)


def pyfluxpro_main(eddypro_full_output, full_output_pyfluxpro, met_data_30_input, met_data_30_pyfluxpro):
    """
    Main function to run PlyFluxPro processing. Calls other functions

    Args:
        eddypro_full_output (str): EddyPro full_output file path
        full_output_pyfluxpro (str): Filename to write the full_output formatted for PyFluxPro
        met_data_30_input (str): Input meteorological file path
        met_data_30_pyfluxpro (str): Meteorological file used as input for PyFluxPro.
    Returns : None
    """
    df = PyFluxProFormat.data_formatting(eddypro_full_output)
    # met_data has data from row index 1. EddyPro full_output will be formatted to have data from row index 1 also.
    # This is step 3a in guide.
    # join met_data and full_output in excel sheet (manual step)

    # write pyfluxpro formatted df to output path
    data_util.write_data(df, full_output_pyfluxpro)
    # copy and rename the met data file
    shutil.copyfile(met_data_30_input, met_data_30_pyfluxpro)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    input_met, input_precip, missing_time, input_soilkey, met_output_file, eddypro_full_output = get_args()
    # run eddypro preprocessing and formatting
    eddypro_main(input_met, input_precip, input_soilkey, missing_time, met_output_file)
    # TODO : Run EddyPro headless here
    full_output_pyfluxpro = cfg.FULL_OUTPUT_PYFLUXPRO
    met_data_30_pyfluxpro = cfg.MET_DATA_30_PYFLUXPRO
    # run pyfluxpro formatting
    pyfluxpro_main(eddypro_full_output, full_output_pyfluxpro, met_output_file, met_data_30_pyfluxpro)
    # manual step of putting met_output_file in one sheet and eddypro_full_output
