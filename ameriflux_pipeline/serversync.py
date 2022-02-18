import os
import pysftp
import stat

from config import Config as cfg


def rsync_data():
    # if there is unknown host error,
    # connect to server using sftp in command line prompt to add host_keys

    remote_path = "/home/shared/loggernet/micromet/Archive"
    local_path = "C:\\workspace-ameriflux\\ameriflux-pipeline\\ameriflux_pipeline\\data\\test"

    with pysftp.Connection(cfg.SFTP_SERVER, username=cfg.SFTP_USERNAME, password=cfg.SFTP_PASSWORD) as sftp:
        sftp.cwd(remote_path)
        for f in sftp.listdir_attr():
            if not stat.S_ISDIR(f.st_mode):
                print("Checking %s..." % f.filename)
                local_file_path = os.path.join(local_path, f.filename)
                if ((not os.path.isfile(local_file_path)) or
                        (f.st_mtime > os.path.getmtime(local_file_path))):
                    print("Downloading %s..." % f.filename)
                    sftp.get(f.filename, local_file_path)


if __name__ == '__main__':
    rsync_data()
