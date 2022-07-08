# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/
"""
File to run post-processing of PyFluxPro run output for Ameriflux submission
"""
import os
import time

from config import Config as cfg
import utils.data_util as data_util
from pyfluxpro.outputformat import OutputFormat


def pyfluxpro_output_ameriflux_processing(l2_run_output, file_meta_data_file, erroring_variable_flag,
                                          erroring_variable_key):
    """
    Function to run PyFluxPro output file formatting for AmeriFlux. Calls other functions

    Args:
        l2_run_output (str): Full filepath of pyfluxpro L2 run output. This typically has a .nc extension
        file_meta_data_file (str) : File containing the meta data, typically the first line of Met data
        erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) have
                                    been renamed to Ameriflux labels. Y is renamed, N if not. By default it is N.
        erroring_variable_key (str): Variable name key used to match the original variable names to Ameriflux names
                                for variables throwing an error in PyFluxPro L1.
                                This is an excel file named L1_erroring_variables.xlsx
    Returns:
        (bool): True if processing is successful, False if not
    """
    ameriflux_df, ameriflux_file_name = OutputFormat.data_formatting(l2_run_output, file_meta_data_file,
                                                                     erroring_variable_flag, erroring_variable_key)
    if ameriflux_file_name is None:
        print("PyFluxPro run output not formatted for Ameriflux")
        return False
    ameriflux_file_name = ameriflux_file_name + '.csv'
    directory_name = os.path.dirname(l2_run_output)
    output_file = os.path.join(directory_name, ameriflux_file_name)
    data_util.write_data(ameriflux_df, output_file)
    return True


if __name__ == '__main__':
    # Main function which calls method for post processing of PyFluxPro output
    # Some preprocessing
    # Filename to write file meta data
    input_filename = os.path.basename(cfg.INPUT_MET)
    file_meta_data_filename = os.path.splitext(input_filename)[0] + '_file_meta.csv'
    # write file_df_meta to this path
    file_meta_data_file = os.path.join(data_util.get_directory(cfg.MASTER_MET), file_meta_data_filename)

    # check if L1 erroring variable names need to be replaced or not
    ameriflux_variable_user_confirmation = cfg.AMERIFLUX_VARIABLE_USER_CONFIRMATION.lower()
    # by default we do not replace the erroring variables to ameriflux naming standards
    erroring_variable_flag = 'N'
    if ameriflux_variable_user_confirmation in ['a', 'ask']:
        print("Enter Y to replace L1 Erroring variable names to Ameriflux standards. Else enter N")
        erroring_variable_flag = input("Enter Y/N : ")
    elif ameriflux_variable_user_confirmation in ['n', 'no']:
        erroring_variable_flag = 'N'
    elif ameriflux_variable_user_confirmation in ['y', 'yes']:
        erroring_variable_flag = 'Y'

    # run ameriflux formatting of pyfluxpro run output
    start = time.time()
    print("Post-processing of PyFluxPro run output has been started")
    is_success = pyfluxpro_output_ameriflux_processing(cfg.L2_AMERIFLUX_RUN_OUTPUT, file_meta_data_file,
                                                       erroring_variable_flag, cfg.L1_AMERIFLUX_ERRORING_VARIABLES_KEY)
    if is_success:
        print("Post-processing of PyFluxPro L2 run output is successful")
    else:
        print("Post-processing of PyFluxPro L2 run output has failed. Aborting")
    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Total elapsed time is : {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
