# Documentation on syncdata module
This document will describe sync modules in syncdata.py and in the GUI enveditor.py

## Overview
- The module is designed for syncing the data between the remote server and local machine
- The module [syncdata.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/utils/syncdata.py) is responsible for this task.
- It can also be controlled by the parameters setting in the enveditor.py GUI.
- Currently, it is only has a single folder to folder syncing option
- Syncing by providing the necessary parameters, such as server url, folder, username, password.

## Instructions to run

### Using GUI
- Currently, it is disabled in enveditor GUI
- Plan to reactivate when the module get improved with more features

### Using command line
- To run, use command ```python syncdata.py```
- The module will not need any input argument but takes the parameters from .env file
    - SFTP_SERVER: URL for the remote server
    - SFTP_USERNAME: username for accessing the remote server
    - SFTP_PASSWORD: password for accessing the remote server
    - SFTP_MET_REMOTE_PATH: remote path for syncing files to local path
    - SFTP_GHG_LOCAL_PATH: local path that remote files get synced