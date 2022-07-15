# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import pysftp
import stat
import paramiko
import logging

from config import Config as cfg

# create log object with current module name
log = logging.getLogger(__name__)


class SyncData:
    @staticmethod
    def sync_data():
        # if there is unknown host error,
        # connect to server using sftp in command line prompt to add host_keys

        if cfg.SFTP_CONFIRMATION.lower() == "y":
            # sync ghg files
            try:
                with pysftp.Connection(cfg.SFTP_SERVER, username=cfg.SFTP_USERNAME, password=cfg.SFTP_PASSWORD) as sftp:
                    sftp.cwd(cfg.SFTP_GHG_REMOTE_PATH)
                    log.info("GHG file sync started.")
                    for file in sftp.listdir_attr():
                        if not stat.S_ISDIR(file.st_mode):
                            # print("Checking %s..." % f.filename)
                            local_file_path = os.path.join(cfg.SFTP_GHG_LOCAL_PATH, file.filename)
                            if ((not os.path.isfile(local_file_path)) or
                                    (file.st_mtime > os.path.getmtime(local_file_path))):
                                log.info("Downloading %s..." % file.filename)
                                sftp.get(file.filename, local_file_path)
                    log.info("GHG file sync completed.")
                    # sync met files
                    sftp.cwd(cfg.SFTP_MET_REMOTE_PATH)
                    log.info("MET file sync started.")
                    for file in sftp.listdir_attr():
                        if not stat.S_ISDIR(file.st_mode):
                            # print("Checking %s..." % f.filename)
                            local_file_path = os.path.join(cfg.SFTP_MET_LOCAL_PATH, file.filename)
                            if ((not os.path.isfile(local_file_path)) or
                                    (file.st_mtime > os.path.getmtime(local_file_path))):
                                log.info("Downloading %s..." % file.filename)
                                sftp.get(file.filename, local_file_path)
                    log.info("GHG file sync completed.")
                sftp.close()
            except (paramiko.ssh_exception.SSHException, AttributeError,
                    paramiko.ssh_exception.AuthenticationException) as e:
                if isinstance(e, paramiko.ssh_exception.SSHException):
                    log.error("Can not connect to the remote URL.")
                    log.error("Checkout the local known_hosts file "
                              "and try to connect using ssh in command prompt first.")
                elif isinstance(e, paramiko.ssh_exception.AuthenticationException):
                    log.error("Authentication Failed.")
                elif isinstance(e, AttributeError):
                    log.error("Can not connect to the remote URL.")
                else:
                    log.error("There was an error in syncing the files.")
