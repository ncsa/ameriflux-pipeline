# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import shutil
from config import Config as cfg
import utils.data_util as data_util

from preprocessor import Preprocessor
from eddyproformat import EddyProFormat
from runeddypro import RunEddypro
from pyfluxpro_format import PyFluxProFormat

def eddypro_preprocessing():
    """
    Main function to run EddyPro processing. Calls other functions

    Args:
        None
    Returns :
        None
    """
    # start preprocessing data
    df, file_meta = Preprocessor.data_preprocess(cfg.INPUT_MET, cfg.INPUT_PRECIP, int(cfg.MISSING_TIME))
    # TODO : check with Bethany - number of decimal places for numerical values
    # write processed df to output path
    data_util.write_data(df, cfg.OUTPUT_MET)

    output_filename = os.path.basename(cfg.OUTPUT_MET)
    # eddypro_output_filename = os.path.splitext(output_filename)[0] + '_eddypro.csv'
    # eddypro_output_file = os.path.join(os.getcwd(), "tests", "data", eddypro_output_filename)
    # start formatting data
    df = EddyProFormat.data_formatting(cfg.OUTPUT_MET, cfg.INPUT_SOIL_KEY, file_meta, cfg.FULL_OUTPUT_MET)
    # write formatted df to output path
    data_util.write_data(df, cfg.FULL_OUTPUT_MET)


def run_eddypro():
    RunEddypro.run_eddypro(eddypro_bin_loc=cfg.EDDYPRO_BIN_LOC, file_name=cfg.EDDYPRO_PROJ_FILE_NAME,
                           project_id=cfg.EDDYPRO_PROJ_ID, project_title=cfg.EDDYPRO_PROJ_TITLE,
                           file_prototype=cfg.EDDYPRO_FILE_PROTOTYPE, proj_file=cfg.EDDYPRO_PROJ_FILE,
                           dyn_metadata_file=cfg.EDDYPRO_DYN_METADATA, out_path=cfg.EDDYPRO_OUTPUT_PATH,
                           data_path=cfg.EDDYPRO_INPUT_GHG_PATH, biom_file=cfg.EDDYPRO_BIOM_FILE)

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
    # run eddypro preprocessing and formatting
    eddypro_preprocessing()

    # run eddypro
    # run_eddypro()

    # grab eddypro full output
    outfile_list = os.listdir(cfg.EDDYPRO_OUTPUT_PATH)
    eddypro_full_outfile = None
    for outfile in outfile_list:
        if 'full_output' in outfile:
            eddypro_full_outfile = os.path.join(cfg.EDDYPRO_OUTPUT_PATH, outfile)

    # run pyfluxpro formatting
    pyfluxpro_main(eddypro_full_outfile, cfg.FULL_OUTPUT_PYFLUXPRO, cfg.OUTPUT_MET, cfg.MET_DATA_30_PYFLUXPRO)
    # manual step of putting met_output_file in one sheet and eddypro_full_output
