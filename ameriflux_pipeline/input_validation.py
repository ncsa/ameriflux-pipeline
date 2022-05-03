# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

'''
Python module to check for user input validation
This module is the first to be called from pre_pyfluxpro
'''

import os
import shutil
import pandas as pd
import time
from datetime import datetime
from validators import url
from data_validation import Validation

from config import Config as cfg

class InputValidation:

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


    @staticmethod
    def server_sync():
        """
        Checks if all env varaibles related to rsync / server sync is valid
        Return True if valid and False if not.
        Args: None
        Returns:
            (bool): True if valid, False if not
        """
        sftp_confirmation = cfg.SFTP_CONFIRMATION
        sftp_confirmation_success = Validation.string_validation(sftp_confirmation)
        if sftp_confirmation_success:
            # sftp_confirmation is a string. Check for valid values
            sftp_confirmation_success = Validation.equality_validation(sftp_confirmation.lower(), 'y') or Validation.equality_validation(sftp_confirmation.lower(), 'n')
        if not sftp_confirmation_success:
            print("Error in SFTP_CONFIRMATION")
            return False
        else:
            # sftp_confirmation is valid. Check for other sync related variables
            sftp_server = cfg.SFTP_SERVER
            sftp_ghg_local_path = cfg.SFTP_GHG_LOCAL_PATH
            sftp_met_local_path = cfg.SFTP_MET_LOCAL_PATH
            sftp_server_success = url(sftp_server)
            sftp_ghg_local_path_success = Validation.path_validation(sftp_ghg_local_path)


