# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import shutil

import pandas as pd

from config import Config as cfg
import utils.data_util as data_util

from master_met.preprocessor import Preprocessor
from eddypro.eddyproformat import EddyProFormat
from eddypro.runeddypro import RunEddypro
from pyfluxpro.pyfluxproformat import PyFluxProFormat
from pyfluxpro.amerifluxformat import AmeriFluxFormat
from pyfluxpro.l1format import L1Format

import pandas.io.formats.excel
pandas.io.formats.excel.header_style = None

GENERATED_DIR = 'generated'


def eddypro_preprocessing():
    """
    Main function to run EddyPro processing. Calls other functions

    Args:
        None
    Returns :
        None
    """
    # start preprocessing data
    df, file_meta = Preprocessor.data_preprocess(cfg.INPUT_MET, cfg.INPUT_PRECIP,
                                                 float(cfg.QC_PRECIP_LOWER), float(cfg.QC_PRECIP_UPPER),
                                                 int(cfg.MISSING_TIME), cfg.USER_CONFIRMATION)
    # TODO : check with Bethany - number of decimal places for numerical values
    # write processed df to output path
    data_util.write_data(df, cfg.MASTER_MET)

    # Write file meta data to another file
    # this can be omitted.
    # The file meta data is passed as a df (file_meta) to eddyproformat. No need for writing to file.
    input_filename = os.path.basename(cfg.INPUT_MET)
    directory_name = os.path.dirname(os.path.dirname(cfg.INPUT_MET))
    file_meta_data_filename = os.path.splitext(input_filename)[0] + '_file_meta.csv'
    # write file_df_meta to this path
    file_meta_data_file = os.path.join(directory_name, GENERATED_DIR, file_meta_data_filename)
    data_util.write_data(file_meta, file_meta_data_file)  # write meta data of file to file. One row.

    # create file for master met formatted for eddypro
    # filename is selected to be master_met_eddypro
    output_filename = os.path.basename(cfg.MASTER_MET)
    directory_name = os.path.dirname(os.path.dirname(cfg.MASTER_MET))
    eddypro_formatted_met_name = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    eddypro_formatted_met_file = os.path.join(directory_name, GENERATED_DIR, eddypro_formatted_met_name)
    # start formatting data
    df = EddyProFormat.data_formatting(cfg.MASTER_MET, cfg.INPUT_SOIL_KEY, file_meta, eddypro_formatted_met_file)
    # write formatted df to output path
    data_util.write_data(df, eddypro_formatted_met_file)

    return eddypro_formatted_met_file, file_meta_data_file


def run_eddypro(eddypro_formatted_met_file):
    RunEddypro.run_eddypro(eddypro_bin_loc=cfg.EDDYPRO_BIN_LOC, proj_file_template=cfg.EDDYPRO_PROJ_FILE_TEMPLATE,
                           proj_file_name=cfg.EDDYPRO_PROJ_FILE_NAME, project_id=cfg.EDDYPRO_PROJ_ID,
                           project_title=cfg.EDDYPRO_PROJ_TITLE, file_prototype=cfg.EDDYPRO_FILE_PROTOTYPE,
                           proj_file=cfg.EDDYPRO_PROJ_FILE, dyn_metadata_file=cfg.EDDYPRO_DYN_METADATA,
                           out_path=cfg.EDDYPRO_OUTPUT_PATH, data_path=cfg.EDDYPRO_INPUT_GHG_PATH,
                           biom_file=eddypro_formatted_met_file)


def pyfluxpro_processing(eddypro_full_output, full_output_pyfluxpro, met_data_30_input, met_data_30_pyfluxpro):
    """
    Main function to run PlyFluxPro processing. Calls other functions

    Args:
        eddypro_full_output (str): EddyPro full_output file path
        full_output_pyfluxpro (str): Filename to write the full_output formatted for PyFluxPro
        met_data_30_input (str): Input meteorological file path
        met_data_30_pyfluxpro (str): Meteorological file used as input for PyFluxPro.
    Returns : None
    """
    full_output_df = PyFluxProFormat.data_formatting(eddypro_full_output)
    # met_data has data from row index 1. EddyPro full_output will be formatted to have data from row index 1 also.
    # This is step 3a in guide.

    # convert timestamp to datetime format so that pyfluxpro can read without error
    full_output_df['TIMESTAMP'][1:] = pd.to_datetime(full_output_df['TIMESTAMP'][1:])

    # write pyfluxpro formatted df to output path
    data_util.write_data(full_output_df, full_output_pyfluxpro)
    # copy and rename the met data file
    shutil.copyfile(met_data_30_input, met_data_30_pyfluxpro)

    met_data_df = pd.read_csv(met_data_30_pyfluxpro)
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
    writer.close()
    print("PyFluxPro input excel sheet saved in ", cfg.PYFLUXPRO_INPUT_SHEET)


def pyfluxpro_ameriflux_processing(input_file, output_file):
    """
    Main function to run PyFluxPro formatting for AmeriFlux. Calls other functions
    Args:
        input_file (str): PyFluxPro input excel sheet file path
        output_file (str): Filename to write the PyFluxPro formatted for AmeriFlux
    Returns : None
    """
    full_output_sheet_name = os.path.splitext(os.path.basename(cfg.FULL_OUTPUT_PYFLUXPRO))[0]
    met_data_sheet_name = os.path.splitext(os.path.basename(cfg.MET_DATA_30_PYFLUXPRO))[0]

    ameriflux_full_output_df, ameriflux_met_df = AmeriFluxFormat.data_formatting(input_file, full_output_sheet_name,
                                                                                 met_data_sheet_name)
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
    writer.close()
    print("AmeriFlux PyFluxPro excel sheet saved in ", output_file)


def pyfluxpro_l1_ameriflux_processing(pyfluxpro_input, l1_input, l1_output, ameriflux_mainstem_key, soils_key):
    """
    Main function to run PyFluxPro L1 control file formatting for AmeriFlux. Calls other functions
    Args:
        pyfluxpro_input (str): A file path for the PyFluxPro input excel sheet formatted for Ameriflux
        l1_input (str): A file path for the input L1.txt. This is the PyFluxPro original L1 control file
        l1_output (str): A file path for the output L1.txt.
                        This is the PyFluxPro L1 control file formatted for AmeriFlux
        ameriflux_mainstem_key (str): Variable name key used to match the original variable names to Ameriflux names
                                        This is an excel file named Ameriflux-Mainstem-Key.xlsx
        soils_key (str): A file path for input soil key sheet. This is used to match the original and
                            AmeriFlux variable names
    Returns: None
    """
    df = L1Format.data_formatting(pyfluxpro_input, l1_input, l1_output, ameriflux_mainstem_key, soils_key)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # run eddypro preprocessing and formatting
    eddypro_formatted_met_file, file_meta_data_file = eddypro_preprocessing()

    # run eddypro
    run_eddypro(eddypro_formatted_met_file)

    # grab eddypro full output
    outfile_list = os.listdir(cfg.EDDYPRO_OUTPUT_PATH)
    eddypro_full_outfile = None
    for outfile in outfile_list:
        if 'full_output' in outfile:
            eddypro_full_outfile = os.path.join(cfg.EDDYPRO_OUTPUT_PATH, outfile)
            # run pyfluxpro formatting
            pyfluxpro_processing(eddypro_full_outfile, cfg.FULL_OUTPUT_PYFLUXPRO, cfg.MASTER_MET,
                                 cfg.MET_DATA_30_PYFLUXPRO)
            break
    # if eddypro full output file not present
    if not eddypro_full_outfile:
        print("EddyPro full output not present")

    # run ameriflux formatting of pyfluxpro input
    if os.path.exists(cfg.PYFLUXPRO_INPUT_SHEET):
        pyfluxpro_ameriflux_processing(cfg.PYFLUXPRO_INPUT_SHEET, cfg.PYFLUXPRO_INPUT_AMERIFLUX)

    # run ameriflux formatting of pyfluxpro L1 control file
    if os.path.exists(cfg.PYFLUXPRO_INPUT_AMERIFLUX) and os.path.exists(cfg.L1_INPUT):
        pyfluxpro_l1_ameriflux_processing(cfg.PYFLUXPRO_INPUT_AMERIFLUX, cfg.L1_INPUT, cfg.L1_AMERIFLUX,
                                          cfg.L1_AMERIFLUX_MAINSTEM_KEY, cfg.INPUT_SOIL_KEY)
