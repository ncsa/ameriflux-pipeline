# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

'''
Python module to check for user input validation
This module is the first to be called from pre_pyfluxpro
'''

from data_validation import DataValidation
from config import Config as cfg

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
            print("Incorrect Server Sync configurations")
            return False

        master_met = InputValidation.master_met()
        if not master_met:
            print("Incorrect Master met configurations")
            return False

        master_met_eddypro = InputValidation.master_met_eddypro()
        if not master_met_eddypro:
            # only one file checked here. print statements in respective method
            return False

        eddypro_headless = InputValidation.eddypro_headless()
        if not eddypro_headless:
            print("Incorrect EddyPro Run configurations")
            return False




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
            print("Error in SFTP_CONFIRMATION")
            return False
        elif DataValidation.equality_validation(sftp_confirmation.lower(), 'y'):
            # sftp_confirmation is valid. Check for other sync related variables
            sftp_server = cfg.SFTP_SERVER
            sftp_ghg_local_path = cfg.SFTP_GHG_LOCAL_PATH
            sftp_met_local_path = cfg.SFTP_MET_LOCAL_PATH
            # check if valid ip or host name
            sftp_server_success = DataValidation.url_validation(sftp_server) or \
                                  DataValidation.domain_validation(sftp_server) or \
                                  DataValidation.ip_validation(sftp_server)
            sftp_ghg_local_path_success = DataValidation.path_validation(sftp_ghg_local_path, 'dir')
            sftp_met_local_path_success = DataValidation.path_validation(sftp_met_local_path, 'dir')
            return sftp_server_success and sftp_ghg_local_path_success and sftp_met_local_path_success


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
        input_met_path_success = DataValidation.path_validation(input_met_path, 'file') and \
                                 DataValidation.filetype_validation(input_met_path, '.csv')
        if not input_met_path_success:
            print("Error in INPUT_MET")
            return False

        input_precip_path = cfg.INPUT_PRECIP
        input_precip_path_success = DataValidation.path_validation(input_precip_path, 'file') and \
                                    DataValidation.filetype_validation(input_precip_path, '.xlsx')
        if not input_precip_path_success:
            print("Error in INPUT_PRECIP")
            return False

        master_met_path = cfg.MASTER_MET
        master_met_path_success = DataValidation.filetype_validation(master_met_path, '.csv')
        if not master_met_path_success:
            print("Error in MASTER_MET")
            return False

        missing_time_user_confirmation = cfg.MISSING_TIME_USER_CONFIRMATION
        missing_time_user_confirmation_success = DataValidation.string_validation(missing_time_user_confirmation)
        if missing_time_user_confirmation_success:
            # sftp_confirmation is a string. Check for valid values
            missing_time_user_confirmation_success = \
                DataValidation.equality_validation(missing_time_user_confirmation.lower(), 'y') or \
                DataValidation.equality_validation(missing_time_user_confirmation.lower(), 'n')
        if not missing_time_user_confirmation_success:
            print("Error in MISSING_TIME_USER_CONFIRMATION")
            return False

        missing_time = cfg.MISSING_TIME
        missing_time_success = DataValidation.integer_validation(missing_time)
        if not missing_time_success:
            print("Error in MISSING_TIME")
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
        input_soil_key_path_success = DataValidation.path_validation(input_soil_key_path, 'file') and \
                                    DataValidation.filetype_validation(input_soil_key_path, '.xlsx')
        if not input_soil_key_path_success:
            print("Error in INPUT_SOIL_KEY")
            return False


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
        eddypro_bin_loc_success = DataValidation.path_validation(eddypro_bin_loc, 'dir') and \
                                  DataValidation.is_empty_dir(eddypro_bin_loc)
        if not eddypro_bin_loc_success:
            print("Error in EDDYPRO_BIN_LOC")
            return False

        eddypro_proj_file_template = cfg.EDDYPRO_PROJ_FILE_TEMPLATE
        eddypro_proj_file_template_success = \
            DataValidation.path_validation(eddypro_proj_file_template, 'file') and \
            DataValidation.filetype_validation(eddypro_proj_file_template, '.eddypro')
        if not eddypro_proj_file_template_success:
            print("Error in EDDYPRO_PROJ_FILE_TEMPLATE")
            return False

        eddypro_proj_file_name = cfg.EDDYPRO_PROJ_FILE_NAME
        eddypro_proj_file_name_success = DataValidation.filetype_validation(eddypro_proj_file_name, '.eddypro')
        if not eddypro_proj_file_template_success:
            print("Error in EDDYPRO_PROJ_FILE_TEMPLATE")
            return False

        eddypro_file_prototype = cfg.EDDYPRO_FILE_PROTOTYPE
        eddypro_file_prototype_success = DataValidation.filetype_validation(eddypro_file_prototype, '.ghg')
        if not eddypro_file_prototype_success:
            print("Error in EDDYPRO_FILE_PROTOTYPE")
            return False

        eddypro_proj_file = cfg.EDDYPRO_PROJ_FILE
        eddypro_proj_file_success = DataValidation.path_validation(eddypro_proj_file, 'file') and \
                                    DataValidation.filetype_validation(eddypro_proj_file, '.metadata')
        if not eddypro_proj_file_success:
            print("Error in EDDYPRO_PROJ_FILE")
            return False

        eddypro_dyn_metadata = cfg.EDDYPRO_DYN_METADATA
        eddypro_dyn_metadata_success = DataValidation.path_validation(eddypro_dyn_metadata, 'file') and \
                                       DataValidation.filetype_validation(eddypro_dyn_metadata, '.csv')
        if not eddypro_dyn_metadata_success:
            print("Error in EDDYPRO_DYN_METADATA")
            return False

        eddypro_input_ghg_path = cfg.EDDYPRO_INPUT_GHG_PATH
        eddypro_input_ghg_path_success = DataValidation.path_validation(eddypro_input_ghg_path, 'dir') and \
                                         DataValidation.is_empty_dir(eddypro_input_ghg_path)
        if not eddypro_input_ghg_path_success:
            print("Error in EDDYPRO_INPUT_GHG_PATH")
            return False

        eddypro_output_path = cfg.EDDYPRO_OUTPUT_PATH
        eddypro_output_path_success = DataValidation.path_validation(eddypro_output_path, 'dir')
        if not eddypro_output_path_success:
            print("Error in EDDYPRO_OUTPUT_PATH")
            return False

        # all validations true
        return True


