import os
import pysftp
import stat
import paramiko

from config import Config as cfg


class SyncData():
    @staticmethod
    def sync_data():
        # if there is unknown host error,
        # connect to server using sftp in command line prompt to add host_keys

        if cfg.SFTP_CONFIRMATION.lower() == "y":
            try:
                with pysftp.Connection(cfg.SFTP_SERVER, username=cfg.SFTP_USERNAME, password=cfg.SFTP_PASSWORD) as sftp:
                    sftp.cwd(cfg.SFTP_REMOTE_PATH)
                    for file in sftp.listdir_attr():
                        if not stat.S_ISDIR(file.st_mode):
                            # print("Checking %s..." % f.filename)
                            local_file_path = os.path.join(cfg.SFTP_LOCAL_PATH, file.filename)
                            if ((not os.path.isfile(local_file_path)) or
                                    (file.st_mtime > os.path.getmtime(local_file_path))):
                                print("Downloading %s..." % file.filename)
                                sftp.get(file.filename, local_file_path)
            except (paramiko.ssh_exception.SSHException, AttributeError, paramiko.ssh_exception.AuthenticationException) as e:
                if isinstance(e, paramiko.ssh_exception.SSHException):
                    print("Error: Can not connect to the remote URL.")
                    print("Error: Checkout the local known_hosts file and try to connect using ssh in command prompt first.")
                elif isinstance(e, paramiko.ssh_exception.AuthenticationException):
                    print("Error: Authentication Failed.")
                elif isinstance(e, AttributeError):
                    print("Error: Can not connect to the remote URL.")
                else:
                    print("There was an error in syncing the files.")
