# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import shutil
import pandas as pd
import time
from datetime import datetime
import logging
import sys

from config import Config as cfg
import utils.data_util as data_util
from utils.syncdata import SyncData as syncdata
from utils.process_validation import DataValidation
from utils.input_validation import InputValidation

from master_met.mastermetprocessor import MasterMetProcessor
from eddypro.eddyproformat import EddyProFormat
from eddypro.runeddypro import RunEddypro
from pyfluxpro.pyfluxproformat import PyFluxProFormat
from pyfluxpro.amerifluxformat import AmeriFluxFormat
from pyfluxpro.l1format import L1Format
from pyfluxpro.l2format import L2Format

import warnings
import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# create and configure logger
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s : %(name)s - %(message)s',
                    handlers=[logging.FileHandler("pre_pyfluxpro.log"), logging.StreamHandler(sys.stdout)])
# create log object with current module name
log = logging.getLogger(__name__)

# create and configure logger
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%dT%H:%M:%S',
                    format='%(asctime)-15s.%(msecs)03dZ %(levelname)-7s [%(threadName)-10s] : %(name)s - %(message)s',
                    handlers=[logging.FileHandler("pre_pyfluxpro.log"), logging.StreamHandler(sys.stdout)])
# create log object with current module name
log = logging.getLogger(__name__)


def input_validation():
    """
    Method to check user input validation from config file
    Args: None
    Returns :
        (bool): True if input data is valid, False if not
    """
    if not InputValidation.server_sync():
        return False
    if not InputValidation.master_met():
        return False
    if not InputValidation.master_met_eddypro():
        return False
    if not InputValidation.eddypro_headless():
        return False
    if not InputValidation.pyfluxpro():
        return False
    if not InputValidation.l1format():
        return False
    if not InputValidation.l2format():
        return False

    log.info("User input validations complete")
    return True


def eddypro_preprocessing(file_meta_data_file):
    """
    Main function to run EddyPro processing. Calls other functions.
    This creates the master met data and formats the same for EddyPro
    Args:
        file_meta_data_file (str) : Filepath to write the meta data, typically the first line of Met data
    Returns :
        eddypro_formatted_met_file (str) : File name of the Met data formatted for eddypro
        site_soil_moisture_variables (dict): Dictionary for soil moisture variable details from Soils key file
        site_soil_temp_variables (dict): Dictionary for soil temperature variable details from Soils key file
    """
    # start preprocessing data
    missing_time = cfg.MISSING_TIME
    qc_precip_lower = cfg.QC_PRECIP_LOWER
    qc_precip_upper = cfg.QC_PRECIP_UPPER

    df, file_meta = \
        MasterMetProcessor.data_preprocess(cfg.INPUT_MET, cfg.INPUT_PRECIP, float(qc_precip_lower),
                                           float(qc_precip_upper), int(missing_time),
                                           cfg.MISSING_TIME_USER_CONFIRMATION)
    if df is None:
        log.error("Creation of master met data has failed.")
        return None
    # write processed df to output path
    data_util.write_data_to_csv(df, cfg.MASTER_MET)

    # Write file meta data to another file
    data_util.write_data_to_csv(file_meta, file_meta_data_file)  # write meta data of file to file. One row.

    # create file for master met formatted for eddypro
    # filename is selected to be master_met_eddypro
    output_filename = os.path.basename(cfg.MASTER_MET)
    eddypro_formatted_met_name = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_formatted_met_file = os.path.join(data_util.get_directory(cfg.MASTER_MET), eddypro_formatted_met_name)
    # start formatting data
    df, site_soil_moisture_variables, site_soil_temp_variables = \
        EddyProFormat.data_formatting(cfg.MASTER_MET, cfg.INPUT_SOIL_KEY, file_meta, eddypro_formatted_met_file)
    if df is None:
        log.error("Eddypro formatting of master met data failed.")
        return None
    # write formatted df to output path
    data_util.write_data_to_csv(df, eddypro_formatted_met_file)

    return eddypro_formatted_met_file, site_soil_moisture_variables, site_soil_temp_variables


def run_eddypro(eddypro_formatted_met_file):
    """
    Method to run EddyPro software headless
    Args:
        eddypro_formatted_met_file (str): File path for Met data file formatted for EddyPro
    Returns: None
    """
    RunEddypro.run_eddypro(eddypro_bin_loc=cfg.EDDYPRO_BIN_LOC, proj_file_template=cfg.EDDYPRO_PROJ_FILE_TEMPLATE,
                           proj_file_name=cfg.EDDYPRO_PROJ_FILE_NAME, project_id=cfg.EDDYPRO_PROJ_ID,
                           project_title=cfg.EDDYPRO_PROJ_TITLE, file_prototype=cfg.EDDYPRO_FILE_PROTOTYPE,
                           proj_file=cfg.EDDYPRO_PROJ_FILE, dyn_metadata_file=cfg.EDDYPRO_DYN_METADATA,
                           out_path=cfg.EDDYPRO_OUTPUT_PATH, data_path=cfg.EDDYPRO_INPUT_GHG_PATH,
                           biom_file=eddypro_formatted_met_file)


def pyfluxpro_processing(eddypro_full_output, full_output_pyfluxpro, met_data_30_input, met_data_30_pyfluxpro):
    """
    Main function to run PyFluxPro processing. Calls other functions

    Args:
        eddypro_full_output (str): EddyPro full_output file path
        full_output_pyfluxpro (str): Filename to write the full_output formatted for PyFluxPro
        met_data_30_input (str): Input meteorological file path
        met_data_30_pyfluxpro (str): Meteorological file used as input for PyFluxPro.
    Returns :
        (bool) : True if pyfluxpro input sheet is successfully created, else False
    """
    full_output_df = PyFluxProFormat.data_formatting(eddypro_full_output)
    if full_output_df is None:
        log.error("Formatting of eddypro full output sheet failed.")
        return False
    # met_data has data from row index 1. EddyPro full_output will be formatted to have data from row index 1 also.
    # This is step 3a in guide.

    # convert timestamp to datetime format so that pyfluxpro can read without error
    full_output_df['TIMESTAMP'][1:] = pd.to_datetime(full_output_df['TIMESTAMP'][1:])

    # write pyfluxpro formatted df to output path
    data_util.write_data_to_csv(full_output_df, full_output_pyfluxpro)
    # copy and rename the met data file
    shutil.copyfile(met_data_30_input, met_data_30_pyfluxpro)

    met_data_df = data_util.read_csv_file(met_data_30_pyfluxpro, dtype='unicode')
    # convert timestamp to datetime format so that pyfluxpro can read without error
    met_data_df['TIMESTAMP'][1:] = pd.to_datetime(met_data_df['TIMESTAMP'][1:])

    full_output_col_list = full_output_df.columns
    met_data_col_list = met_data_df.columns
    # join met_data and full_output in excel sheet
    # write df and met_data df to an excel spreadsheet in two separate tabs
    full_output_sheet_name = os.path.splitext(os.path.basename(full_output_pyfluxpro))[0]
    met_data_sheet_name = os.path.splitext(os.path.basename(met_data_30_pyfluxpro))[0]

    writer = pd.ExcelWriter(cfg.PYFLUXPRO_INPUT_SHEET, engine='xlsxwriter',
                            datetime_format='yyyy/mm/dd HH:MM',
                            date_format='yyyy/mm/dd',
                            engine_kwargs={'options': {'strings_to_numbers': True}})

    # remove header so as to remove built-in formatting of xlsxwriter
    full_output_df.to_excel(writer, sheet_name=full_output_sheet_name, index=False, header=False, startrow=1)
    met_data_df.to_excel(writer, sheet_name=met_data_sheet_name, index=False, header=False, startrow=1)

    full_output_worksheet = writer.sheets[full_output_sheet_name]
    met_data_worksheet = writer.sheets[met_data_sheet_name]

    for idx, val in enumerate(full_output_col_list):
        full_output_worksheet.write(0, idx, val)
    for idx, val in enumerate(met_data_col_list):
        met_data_worksheet.write(0, idx, val)

    writer.save()
    log.info("PyFluxPro input excel sheet saved in %s", cfg.PYFLUXPRO_INPUT_SHEET)
    # eddypro full output sheet formatting and pyfluxpro input sheet creation is successful
    return True


def pyfluxpro_ameriflux_processing(input_file, output_file):
    """
    Function to format PyFluxPro input excel sheet for AmeriFlux. Calls other functions
    Args:
        input_file (str): PyFluxPro input excel sheet file path
        output_file (str): Filename to write the PyFluxPro formatted for AmeriFlux
    Returns :
        (bool) : True if pyfluxpro input sheet is successfully created, else False
    """
    full_output_sheet_name = os.path.splitext(os.path.basename(cfg.FULL_OUTPUT_PYFLUXPRO))[0]
    met_data_sheet_name = os.path.splitext(os.path.basename(cfg.MET_DATA_30_PYFLUXPRO))[0]

    ameriflux_full_output_df, ameriflux_met_df = AmeriFluxFormat.data_formatting(input_file, full_output_sheet_name,
                                                                                 met_data_sheet_name)
    if ameriflux_full_output_df is None:
        log.error("Processing of full_output for Ameriflux failed")
        return False
    if ameriflux_met_df is None:
        log.error("Processing of Met_data_30 for Ameriflux failed")
        return False
    ameriflux_full_output_df_col_list = ameriflux_full_output_df.columns
    ameriflux_met_df_col_list = ameriflux_met_df.columns

    # write df and met_data df to an excel spreadsheet in two separate tabs
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter', datetime_format='yyyy/mm/dd HH:MM',
                            date_format='yyyy/mm/dd', engine_kwargs={'options': {'strings_to_numbers': True}})

    # remove header so as to remove built-in formatting of xlsxwriter
    ameriflux_full_output_df.to_excel(writer, sheet_name=full_output_sheet_name, index=False, header=False, startrow=1)
    ameriflux_met_df.to_excel(writer, sheet_name=met_data_sheet_name, index=False, header=False, startrow=1)

    full_output_worksheet = writer.sheets[full_output_sheet_name]
    met_data_worksheet = writer.sheets[met_data_sheet_name]
    for idx, val in enumerate(ameriflux_full_output_df_col_list):
        full_output_worksheet.write(0, idx, val)
    for idx, val in enumerate(ameriflux_met_df_col_list):
        met_data_worksheet.write(0, idx, val)

    writer.save()
    log.info("AmeriFlux PyFluxPro excel sheet saved in %s", output_file)
    # all processing successful
    return True


def pyfluxpro_l1_ameriflux_processing(pyfluxpro_input, l1_mainstem, l1_ameriflux_only, ameriflux_mainstem_key,
                                      file_meta_data_file, l1_run_output, l1_ameriflux_output,
                                      erroring_variable_flag, erroring_variable_key,
                                      site_soil_moisture_variables, site_soil_temp_variables):
    """
    Main function to run PyFluxPro L1 control file formatting for AmeriFlux. Calls other functions
    Args:
        pyfluxpro_input (str): A file path for the PyFluxPro input excel sheet formatted for Ameriflux
        l1_mainstem (str): A file path for the input L1.txt. This is the PyFluxPro original L1 control file
        l1_ameriflux_only (str): A file path for the L1.txt that contains only Ameriflux-friendly variables
        ameriflux_mainstem_key (str): Variable name key used to match the original variable names to Ameriflux names
                                    This is an excel file named Ameriflux-Mainstem-Key.xlsx
        file_meta_data_file (str) : File containing the meta data, typically the first line of Met data
        l1_run_output (str): A file path for the output of L1 run. This typically has .nc extension
        l1_ameriflux_output (str): A file path for the generated L1.txt that is formatted for Ameriflux standards
        erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) are
                                    renamed to Ameriflux labels in L1. Y is renamed, N if not. By default it is N.
        erroring_variable_key (str): Variable name key used to match the original variable names to Ameriflux names
                                    for variables throwing an error in PyFluxPro L1.
                                    This is an excel file named L1_erroring_variables.xlsx
        site_soil_moisture_variables(dict): Dictionary for soil moisture variable details from Soils key file
        site_soil_temp_variables (dict): Dictionary for soil temperature variable details from Soils key file

    Returns:
        pyfluxpro_ameriflux_label (dict): Mapping of pyfluxpro-friendly label to Ameriflux-friendly labels for
                                          variables in L1_Ameriflux.txt
        erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) have been
                                     renamed to Ameriflux labels. Y is renamed, N if not. By default it is N.
    """
    pyfluxpro_ameriflux_labels = \
        L1Format.data_formatting(pyfluxpro_input, l1_mainstem, l1_ameriflux_only, ameriflux_mainstem_key,
                                 file_meta_data_file, l1_run_output, l1_ameriflux_output,
                                 erroring_variable_flag, erroring_variable_key,
                                 site_soil_moisture_variables, site_soil_temp_variables)
    return pyfluxpro_ameriflux_labels


def pyfluxpro_l2_ameriflux_processing(pyfluxpro_ameriflux_label, l2_mainstem, l2_ameriflux_only,
                                      l1_run_output, l2_run_output, l2_ameriflux_output):
    """
        Main function to run PyFluxPro L2 control file formatting for AmeriFlux. Calls other functions

        Args:
            pyfluxpro_ameriflux_label (dict): Mapping of pyfluxpro-friendly label to Ameriflux-friendly labels for
                                            variables in l1_ameriflux_output
            l2_mainstem (str): A file path for the input L2.txt. This is the PyFluxPro original L2 control file
            l2_ameriflux_only (str): A file path for the L2.txt that contains only Ameriflux-friendly variables
            l1_run_output (str): A file path for the output of L1 run. This typically has .nc extension
            l2_run_output (str): A file path for the output of L2 run. This typically has .nc extension
            l2_ameriflux_output (str): A file path for the generated L2.txt that is formatted for Ameriflux standards
        Returns:
            None
    """
    is_success = L2Format.data_formatting(pyfluxpro_ameriflux_label, l2_mainstem, l2_ameriflux_only, l1_run_output,
                                          l2_run_output, l2_ameriflux_output)
    return is_success


def pre_processing(file_meta_data_file, erroring_variable_flag):
    """
       Function to run Master met, EddyPro and PyFluxPro file formatting for AmeriFlux. Calls other functions

       Args:
           file_meta_data_file (str): Filepath to write the meta data, typically the first line of Met data
           erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) have
                                       been renamed to Ameriflux labels. Y is renamed, N if not. By default it is N.
       Returns:
           (bool): True if method runs successfully, False if not
    """
    # sync data from the server
    syncdata.sync_data()

    # run eddypro preprocessing and formatting
    eddypro_formatted_met_file, site_soil_moisture_variables, site_soil_temp_variables = \
        eddypro_preprocessing(file_meta_data_file)

    if not os.path.exists(eddypro_formatted_met_file):
        # return failure
        log.error("EddyPro Processing failed")
        return False

    # archive old eddypro output path
    outfile_list = os.listdir(cfg.EDDYPRO_OUTPUT_PATH)
    if len(outfile_list) > 0:
        # eddypro output dir not empty. move all files
        source_dir = cfg.EDDYPRO_OUTPUT_PATH
        # create a dir with timestamp name in the same path
        dest_dir = os.path.dirname(cfg.EDDYPRO_OUTPUT_PATH) + '_run_result_' + datetime.now().strftime('%Y-%m-%d_%H-%M')
        os.makedirs(dest_dir)
        for f in outfile_list:
            # move each file
            source = os.path.join(source_dir, f)
            dest = os.path.join(dest_dir, f)
            shutil.move(source, dest)

    # run eddypro
    run_eddypro(eddypro_formatted_met_file)

    # grab eddypro full output
    outfile_list = os.listdir(cfg.EDDYPRO_OUTPUT_PATH)
    eddypro_full_outfile = None
    is_pyfluxpro_processing_success = False
    for outfile in outfile_list:
        if 'full_output' in outfile:
            eddypro_full_outfile = os.path.join(cfg.EDDYPRO_OUTPUT_PATH, outfile)
            # filetype validation for eddypro_full_outfile
            if not DataValidation.filetype_validation(eddypro_full_outfile, '.csv'):
                log.error(".csv extension expected for file %s", eddypro_full_outfile)
                # get the next full_output sheet if exists
                continue
            # run pyfluxpro formatting
            is_pyfluxpro_processing_success = pyfluxpro_processing(eddypro_full_outfile, cfg.FULL_OUTPUT_PYFLUXPRO,
                                                                   cfg.MASTER_MET, cfg.MET_DATA_30_PYFLUXPRO)
            if is_pyfluxpro_processing_success:
                # pyfluxpro formatting is success, break out of loop.
                break

    # if eddypro full output file not present
    if not eddypro_full_outfile:
        log.error('-' * 10 + "EddyPro full output not present. Aborting" + '-' * 10)
        # return failure
        return False
    if not is_pyfluxpro_processing_success:
        log.error('-' * 10 + "PyFluxpro processing failed. Aborting" + '-' * 10)
        return False

    # run ameriflux formatting of pyfluxpro input
    if os.path.exists(cfg.PYFLUXPRO_INPUT_SHEET):
        is_pyfluxpro_ameriflux_processing_success = \
            pyfluxpro_ameriflux_processing(cfg.PYFLUXPRO_INPUT_SHEET, cfg.PYFLUXPRO_INPUT_AMERIFLUX)
        if not is_pyfluxpro_ameriflux_processing_success:
            log.error('-' * 10 + "PyFluxpro input sheet formatting for Ameriflux failed. Aborting" + '-' * 10)
            return False  # return failure
    else:
        log.error('-' * 10 + "%s path does not exist. Aborting" + '-' * 10, cfg.PYFLUXPRO_INPUT_SHEET)
        return False  # return failure

    # run ameriflux formatting of pyfluxpro L1 control file
    pyfluxpro_ameriflux_labels = \
        pyfluxpro_l1_ameriflux_processing(cfg.PYFLUXPRO_INPUT_AMERIFLUX, cfg.L1_MAINSTEM_INPUT,
                                          cfg.L1_AMERIFLUX_ONLY_INPUT, cfg.L1_AMERIFLUX_MAINSTEM_KEY,
                                          file_meta_data_file, cfg.L1_AMERIFLUX_RUN_OUTPUT, cfg.L1_AMERIFLUX,
                                          erroring_variable_flag, cfg.L1_AMERIFLUX_ERRORING_VARIABLES_KEY,
                                          site_soil_moisture_variables, site_soil_temp_variables)
    if pyfluxpro_ameriflux_labels is None:
        log.error('-' * 10 + "PyFluxPro L1 processing failed. Aborting" + '-' * 10)
        return False  # return failure

    # run ameriflux formatting of pyfluxpro L2 control file
    is_success = pyfluxpro_l2_ameriflux_processing(pyfluxpro_ameriflux_labels, cfg.L2_MAINSTEM_INPUT,
                                                   cfg.L2_AMERIFLUX_ONLY_INPUT, cfg.L1_AMERIFLUX_RUN_OUTPUT,
                                                   cfg.L2_AMERIFLUX_RUN_OUTPUT, cfg.L2_AMERIFLUX)
    if is_success:
        log.info("Run PyFluxPro V3.3.2 with the generated L1 and L2 control files")
        log.info("Generated control files in %s %s", cfg.L1_AMERIFLUX, cfg.L2_AMERIFLUX)
        return True  # all processing done return success
    else:
        log.error('-' * 10 + "PyFluxPro L2 processing failed. Aborting" + '-' * 10)
        return False  # return failure


def main():
    """
    Main function to run. Calls other function
    Args : None
    Returns : None
    """
    # Main function
    is_valid_config = input_validation()
    if not is_valid_config:
        log.error('-' * 10 + "Check .env file and fix configurations. Aborting" + '-' * 10)
        return

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

    # run pre-processing steps of PyFluxPro L1 an L2
    start = time.time()
    log.info("Pre-processing of PyFluxPro run output has been started")

    is_success = pre_processing(file_meta_data_file, erroring_variable_flag)
    if is_success:
        log.info("Successfully completed pre-processing of PyFluxPro L1 and L2")
    else:
        log.error('-' * 10 + "Pre-processing resulted in an error." + '-' * 10)

    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    log.info("Total elapsed time is : {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


if __name__ == '__main__':
    log.info('-' * 50)
    log.info("############# Process Started #############")
    # Call main function
    main()
