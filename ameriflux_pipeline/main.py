# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import argparse
import utils.data_util as data_util

from preprocessor import Preprocessor


def perform_data_processing(input_path, output_path, missing_time_threshold, meta_data_path):
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
    parser.add_argument("--missingTime", action="store",
                        default=96,
                        help="Number of 30min timeslot threshold to ask for user confirmation")
    parser.add_argument("--metadata", action="store",
                        default=os.path.join(os.getcwd(), "tests", "data", "FLUXSB_EC.dat.meta.csv"),
                        help="meta data file path")

    # parse arguments

    args = parser.parse_args()

    # start preprocessing data
    df = perform_data_processing(args.input, args.output, args.missingTime, args.metadata)

    # write processed df to output path
    data_util.write_dataframe_to_csv(df, args.output)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()