# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

'''
Python module to check for user input validation
This module is the first to be called from pre_pyfluxpro
'''

from config import Config as cfg
import logging
from utils.process_validation import DataValidation
import utils.data_util as data_util

# create log object with current module name
log = logging.getLogger(__name__)


class InputValidation:
    '''
    Class to implement input validation
    '''

    @staticmethod
    def validate():
        """
        Reads all configuration variables / user inputs and checks for validity
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        server_sync = InputValidation.server_sync()
        if not server_sync:
            log.error("Please check Server Sync input variables")
            return False

        master_met = InputValidation.master_met()
        if not master_met:
            log.error("Please check Master met input variables")
            return False

        master_met_eddypro = InputValidation.master_met_eddypro()
        if not master_met_eddypro:
            # only one file checked here. print statements in respective method
            return False

        eddypro_headless = InputValidation.eddypro_headless()
        if not eddypro_headless:
            log.error("Please check EddyPro Run input variables")
            return False

        pyfluxpro = InputValidation.pyfluxpro()
        if not pyfluxpro:
            log.error("Please check PyFluxpro input sheets input variables")
            return False

        l1format = InputValidation.l1format()
        if not l1format:
            log.error("Please check Pyfluxpro L1 variables")
            return False

        l2format = InputValidation.l2format()
        if not l2format:
            log.error("Please check Pyfluxpro L2 variables")
            return False

        # all validations passed
        return True

    @staticmethod
    def server_sync():
        """
        Checks if all env variables related to rsync / server sync is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        sftp_confirmation = cfg.SFTP_CONFIRMATION
        sftp_confirmation_success = DataValidation.string_validation(sftp_confirmation)
        if sftp_confirmation_success:
            # sftp_confirmation is a string. Check for valid values
            sftp_confirmation_success = DataValidation.equality_validation(sftp_confirmation.lower(), 'y') or \
                                        DataValidation.equality_validation(sftp_confirmation.lower(), 'n')
        if not sftp_confirmation_success:
            log.error("Expected Y or N for SFTP_CONFIRMATION")
            return False
        elif DataValidation.equality_validation(sftp_confirmation.lower(), 'y'):
            # sftp_confirmation is valid. Server sync is required. Check for other sync related variables
            sftp_server = cfg.SFTP_SERVER
            sftp_ghg_local_path = cfg.SFTP_GHG_LOCAL_PATH
            sftp_met_local_path = cfg.SFTP_MET_LOCAL_PATH
            # check if valid ip or host name
            sftp_server_success = \
                DataValidation.url_validation(sftp_server) or DataValidation.domain_validation(sftp_server) or \
                DataValidation.ip_validation(sftp_server)
            sftp_ghg_local_path_success = DataValidation.path_validation(sftp_ghg_local_path, 'dir')
            sftp_met_local_path_success = DataValidation.path_validation(sftp_met_local_path, 'dir')
            return sftp_server_success and sftp_ghg_local_path_success and sftp_met_local_path_success

        else:
            # Server sync not required. sftp_confirmation is n
            return True

    @staticmethod
    def master_met():
        """
        Checks if all env variables related to creation of master met data is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        input_met_path = cfg.INPUT_MET
        input_met_path_success = \
            DataValidation.path_validation(input_met_path, 'file') and \
            DataValidation.filetype_validation(input_met_path, '.csv')
        if not input_met_path_success:
            log.error("Expected csv file for INPUT_MET")
            return False

        input_precip_path = cfg.INPUT_PRECIP
        input_precip_path_success = \
            DataValidation.path_validation(input_precip_path, 'file') and \
            (DataValidation.filetype_validation(input_precip_path, '.xlsx') or
             DataValidation.filetype_validation(input_precip_path, '.xls'))
        if not input_precip_path_success:
            log.error("Expected excel file for INPUT_PRECIP")
            return False

        master_met_path = cfg.MASTER_MET
        master_met_dir = data_util.get_directory(master_met_path)
        master_met_path_success = \
            DataValidation.path_validation(master_met_dir, 'dir') and \
            DataValidation.filetype_validation(master_met_path, '.csv')
        if not master_met_path_success:
            log.error("Expected csv file for MASTER_MET")
            return False

        missing_time_user_confirmation = cfg.MISSING_TIME_USER_CONFIRMATION
        missing_time_user_confirmation_success = DataValidation.string_validation(missing_time_user_confirmation)
        if missing_time_user_confirmation_success:
            # sftp_confirmation is a string. Check for valid values
            missing_time_user_confirmation_success = \
                DataValidation.equality_validation(missing_time_user_confirmation.lower(), 'y') or \
                DataValidation.equality_validation(missing_time_user_confirmation.lower(), 'n') or \
                DataValidation.equality_validation(missing_time_user_confirmation.lower(), 'a')
        if not missing_time_user_confirmation_success:
            log.error("Expected Y / N / A for MISSING_TIME_USER_CONFIRMATION")
            return False

        missing_time = cfg.MISSING_TIME
        missing_time_success = DataValidation.integer_validation(missing_time)
        if not missing_time_success:
            log.error("Expected integer for MISSING_TIME")
            return False

        qc_precip_lower = cfg.QC_PRECIP_LOWER
        qc_precip_lower_success = DataValidation.float_validation(qc_precip_lower)
        if not qc_precip_lower_success:
            log.error("Expected floating point for QC_PRECIP_LOWER")
            return False
        qc_precip_upper = cfg.QC_PRECIP_UPPER
        qc_precip_upper_success = DataValidation.float_validation(qc_precip_upper)
        if not qc_precip_upper_success:
            log.error("Expected floating point for QC_PRECIP_UPPER")
            return False

        # all validations true
        return True

    @staticmethod
    def master_met_eddypro():
        """
        Checks if all env variables related to formatting of master met data for EddyPro is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        input_soil_key_path = cfg.INPUT_SOIL_KEY
        input_soil_key_path_success = \
            DataValidation.path_validation(input_soil_key_path, 'file') and \
            (DataValidation.filetype_validation(input_soil_key_path, '.xlsx') or
             DataValidation.filetype_validation(input_soil_key_path, '.xls'))
        if not input_soil_key_path_success:
            log.error("Expected excel file for INPUT_SOIL_KEY")
            return False
        else:
            return True

    @staticmethod
    def eddypro_headless():
        """
        Checks if all env variables related to EddyPro Run is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        eddypro_bin_loc = cfg.EDDYPRO_BIN_LOC
        eddypro_bin_loc_success = \
            DataValidation.path_validation(eddypro_bin_loc, 'dir') and \
            not DataValidation.is_empty_dir(eddypro_bin_loc) and \
            DataValidation.is_file_in_dir('eddypro_rp', eddypro_bin_loc)
        if not eddypro_bin_loc_success:
            log.error("Expected directory containing eddypro exec file for EDDYPRO_BIN_LOC")
            return False

        eddypro_proj_file_template = cfg.EDDYPRO_PROJ_FILE_TEMPLATE
        eddypro_proj_file_template_success = \
            DataValidation.path_validation(eddypro_proj_file_template, 'file') and \
            DataValidation.filetype_validation(eddypro_proj_file_template, '.eddypro')
        if not eddypro_proj_file_template_success:
            log.error("Expected .eddypro file for EDDYPRO_PROJ_FILE_TEMPLATE")
            return False

        eddypro_proj_file_name = cfg.EDDYPRO_PROJ_FILE_NAME
        eddypro_proj_file_name_success = DataValidation.filetype_validation(eddypro_proj_file_name, '.eddypro')
        if not eddypro_proj_file_name_success:
            log.error("Expected .eddypro file for EDDYPRO_PROJ_FILE_TEMPLATE")
            return False

        eddypro_file_prototype = cfg.EDDYPRO_FILE_PROTOTYPE
        eddypro_file_prototype_success = DataValidation.filetype_validation(eddypro_file_prototype, '.ghg')
        if not eddypro_file_prototype_success:
            log.error("Expected .ghg file for EDDYPRO_FILE_PROTOTYPE")
            return False

        eddypro_proj_file = cfg.EDDYPRO_PROJ_FILE
        eddypro_proj_file_success = \
            DataValidation.path_validation(eddypro_proj_file, 'file') and \
            DataValidation.filetype_validation(eddypro_proj_file, '.metadata')
        if not eddypro_proj_file_success:
            log.error("Expected .metadata file for EDDYPRO_PROJ_FILE")
            return False

        eddypro_dyn_metadata = cfg.EDDYPRO_DYN_METADATA
        eddypro_dyn_metadata_success = \
            DataValidation.path_validation(eddypro_dyn_metadata, 'file') and \
            DataValidation.filetype_validation(eddypro_dyn_metadata, '.csv')
        if not eddypro_dyn_metadata_success:
            log.error("Expected .csv file for EDDYPRO_DYN_METADATA")
            return False

        eddypro_input_ghg_path = cfg.EDDYPRO_INPUT_GHG_PATH
        eddypro_input_ghg_path_success = \
            DataValidation.path_validation(eddypro_input_ghg_path, 'dir') and \
            not DataValidation.is_empty_dir(eddypro_input_ghg_path)
        if not eddypro_input_ghg_path_success:
            log.error("Expected a directory containing ghg files for EDDYPRO_INPUT_GHG_PATH")
            return False

        eddypro_output_path = cfg.EDDYPRO_OUTPUT_PATH
        eddypro_output_path_success = DataValidation.path_validation(eddypro_output_path, 'dir')
        if not eddypro_output_path_success:
            log.error("Expected a directory for EDDYPRO_OUTPUT_PATH")
            return False

        # all validations true
        return True

    @staticmethod
    def pyfluxpro():
        """
        Checks if all env variables related to creation of pyfluxpro input sheets is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        full_output_pyfluxpro = cfg.FULL_OUTPUT_PYFLUXPRO
        full_output_pyfluxpro_dir = data_util.get_directory(full_output_pyfluxpro)
        full_output_pyfluxpro_success = \
            DataValidation.path_validation(full_output_pyfluxpro_dir, 'dir') and \
            DataValidation.filetype_validation(full_output_pyfluxpro, '.csv')
        if not full_output_pyfluxpro_success:
            log.error("Expected a csv file for FULL_OUTPUT_PYFLUXPRO")

        met_data_30_pyfluxpro = cfg.MET_DATA_30_PYFLUXPRO
        met_data_30_pyfluxpro_dir = data_util.get_directory(met_data_30_pyfluxpro)
        met_data_30_pyfluxpro_success = \
            DataValidation.path_validation(met_data_30_pyfluxpro_dir, 'dir') and \
            DataValidation.filetype_validation(met_data_30_pyfluxpro, '.csv')
        if not met_data_30_pyfluxpro_success:
            log.error("Expected a csv file for MET_DATA_30_PYFLUXPRO")

        pyfluxpro_input_sheet = cfg.PYFLUXPRO_INPUT_SHEET
        pyfluxpro_input_sheet_dir = data_util.get_directory(pyfluxpro_input_sheet)
        pyfluxpro_input_sheet_success = \
            DataValidation.path_validation(pyfluxpro_input_sheet_dir, 'dir') and \
            DataValidation.filetype_validation(pyfluxpro_input_sheet, '.xlsx')
        if not pyfluxpro_input_sheet_success:
            log.error("Expected an excel file for PYFLUXPRO_INPUT_SHEET")

        pyfluxpro_input_ameriflux = cfg.PYFLUXPRO_INPUT_AMERIFLUX
        pyfluxpro_input_ameriflux_dir = data_util.get_directory(pyfluxpro_input_ameriflux)
        pyfluxpro_input_ameriflux_success = \
            DataValidation.path_validation(pyfluxpro_input_ameriflux_dir, 'dir') and \
            DataValidation.filetype_validation(pyfluxpro_input_ameriflux, '.xlsx')
        if not pyfluxpro_input_ameriflux_success:
            log.error("Expected an excel file for PYFLUXPRO_INPUT_AMERIFLUX")

        # all validations true
        return True

    @staticmethod
    def l1format():
        """
        Checks if all env variables related to creation of pyfluxpro L1 is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        l1_mainstem_input = cfg.L1_MAINSTEM_INPUT
        l1_mainstem_input_success = \
            DataValidation.path_validation(l1_mainstem_input, 'file') and \
            DataValidation.filetype_validation(l1_mainstem_input, '.txt')
        if not l1_mainstem_input_success:
            log.error("Check txt file for L1_MAINSTEM_INPUT")
            return False

        l1_ameriflux_only_input = cfg.L1_AMERIFLUX_ONLY_INPUT
        l1_ameriflux_only_input_success = \
            DataValidation.path_validation(l1_ameriflux_only_input, 'file') and \
            DataValidation.filetype_validation(l1_ameriflux_only_input, '.txt')
        if not l1_ameriflux_only_input_success:
            log.error("Check txt file for L1_AMERIFLUX_ONLY_INPUT")
            return False

        l1_ameriflux_mainstem_key = cfg.L1_AMERIFLUX_MAINSTEM_KEY
        l1_ameriflux_mainstem_key_success = \
            DataValidation.path_validation(l1_ameriflux_mainstem_key, 'file') and \
            (DataValidation.filetype_validation(l1_ameriflux_mainstem_key, '.xlsx') or
             DataValidation.filetype_validation(l1_ameriflux_mainstem_key, '.xls'))
        if not l1_ameriflux_mainstem_key_success:
            log.error("Check excel file for L1_AMERIFLUX_MAINSTEM_KEY")
            return False

        l1_ameriflux_run_output = cfg.L1_AMERIFLUX_RUN_OUTPUT
        l1_ameriflux_run_output_success = \
            DataValidation.path_validation(data_util.get_directory(l1_ameriflux_run_output), 'dir') and \
            DataValidation.filetype_validation(l1_ameriflux_run_output, '.nc')
        if not l1_ameriflux_run_output_success:
            log.error("Check netCDF .nc file for L1_AMERIFLUX_RUN_OUTPUT")
            return False

        l1_ameriflux = cfg.L1_AMERIFLUX
        l1_ameriflux_success = \
            DataValidation.path_validation(data_util.get_directory(l1_ameriflux), 'dir') and \
            DataValidation.filetype_validation(l1_ameriflux, '.txt')
        if not l1_ameriflux_success:
            log.error("Check txt file for L1_AMERIFLUX")
            return False

        ameriflux_variable_user_confirmation = cfg.AMERIFLUX_VARIABLE_USER_CONFIRMATION
        ameriflux_variable_user_confirmation_success = \
            DataValidation.string_validation(ameriflux_variable_user_confirmation)
        if ameriflux_variable_user_confirmation_success:
            # user_confirmation is a string. Check for valid values
            ameriflux_variable_user_confirmation_success = \
                DataValidation.equality_validation(ameriflux_variable_user_confirmation.lower(), 'y') or \
                DataValidation.equality_validation(ameriflux_variable_user_confirmation.lower(), 'n') or \
                DataValidation.equality_validation(ameriflux_variable_user_confirmation.lower(), 'a')
        if not ameriflux_variable_user_confirmation_success:
            log.error("Expected Y / N / A for AMERIFLUX_VARIABLE_USER_CONFIRMATION")
            return False

        if DataValidation.equality_validation(ameriflux_variable_user_confirmation.lower(), 'n'):
            # erroring variables key is only read if the user confirmation for replacing pyfluxpro labels is no
            # erroring variables key contains which variables should not be replaced.
            l1_ameriflux_erroring_variables_key = cfg.L1_AMERIFLUX_ERRORING_VARIABLES_KEY
            l1_ameriflux_erroring_variables_key_success = \
                DataValidation.path_validation(data_util.get_directory(l1_ameriflux_erroring_variables_key), 'dir') \
                and (DataValidation.filetype_validation(l1_ameriflux_erroring_variables_key, '.xlsx') or
                     DataValidation.filetype_validation(l1_ameriflux_erroring_variables_key, '.xls'))
            if not l1_ameriflux_erroring_variables_key_success:
                log.error("Expected an excel file for L1_AMERIFLUX_ERRORING_VARIABLES_KEY")
                return False

        # all validations true
        return True

    @staticmethod
    def l2format():
        """
        Checks if all env variables related to creation of pyfluxpro L2 is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        l2_mainstem_input = cfg.L2_MAINSTEM_INPUT
        l2_mainstem_input_success = \
            DataValidation.path_validation(l2_mainstem_input, 'file') and \
            DataValidation.filetype_validation(l2_mainstem_input, '.txt')
        if not l2_mainstem_input_success:
            log.error("Check txt file for L2_MAINSTEM_INPUT")
            return False

        l2_ameriflux_only_input = cfg.L2_AMERIFLUX_ONLY_INPUT
        l2_ameriflux_only_input_success = \
            DataValidation.path_validation(l2_ameriflux_only_input, 'file') and \
            DataValidation.filetype_validation(l2_ameriflux_only_input, '.txt')
        if not l2_ameriflux_only_input_success:
            log.error("Check txt file for L2_AMERIFLUX_ONLY_INPUT")
            return False

        l2_ameriflux_run_output = cfg.L2_AMERIFLUX_RUN_OUTPUT
        l2_ameriflux_run_output_success = \
            DataValidation.path_validation(data_util.get_directory(l2_ameriflux_run_output), 'dir') and \
            DataValidation.filetype_validation(l2_ameriflux_run_output, '.nc')
        if not l2_ameriflux_run_output_success:
            log.error("Check netCDF .nc file for L2_AMERIFLUX_RUN_OUTPUT")
            return False

        l2_ameriflux = cfg.L2_AMERIFLUX
        l2_ameriflux_success = \
            DataValidation.path_validation(data_util.get_directory(l2_ameriflux), 'dir') and \
            DataValidation.filetype_validation(l2_ameriflux, '.txt')
        if not l2_ameriflux_success:
            log.error("Check txt file for L2_AMERIFLUX")
            return False

        # all validations true
        return True
