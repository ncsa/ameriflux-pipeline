# Documentation on enveditor
This document will describe the GUI enveditor application.

## Overview 
- The ameriflux_pipeline module uses several user inputs and settings to run. 
- The command ```python enveditor.py``` launches a GUI that is used to configure the settings and user inputs required to run the pipeline.
- The GUI application is implemented using [tkinter](https://docs.python.org/3/library/tk.html) python library.
- Using the GUI, the user is able to browse through files, choose and type in various settings.
- On clicking the "Save" button, a .env file is generated in the working directory.
- This .env file is used by the pipeline (pre_pyfluxpro and post_pyfluxpro modules) to read in the user settings and runs the pipeline accordingly.
- [Sync module](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/utils/syncdata.md) is skipped by default.
- If the Sync module needs to be run, the user inputs can be configured by setting SHOW_DATA_SYNC to be True in [enveditor.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/enveditor.py#L29)
