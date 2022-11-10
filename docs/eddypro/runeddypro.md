# Documentation on runeddypro module
This document will describe runeddypro.py

## Overview
- The runeddypro module is for running eddypro application in the pipeline without any human interaction.
- The module [runeddypro.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/eddypro/runeddypro.py) 
  is responsible for this task.
- The process only works in Windows or Mac; Linux or Mac with M1 chips are not supported
- EddyPro is an independent software application. It will be run in a headless manner (initiated programmatically without human interaction) by the module.
- The log of the process will be recorded in pre_fylufxpro.log with 'eddypro.runeddypro' header.
- Each eddypro run will also generated a timestamped log file in the 'EDDYPRO_OUTPUT_PATH'.
- The runeddypro module can be run with a pipeline.py GUI.

## How to run

### Set parameters
- There are serveral parameters to set to run the module.
- The parameters can be set using [enveditor.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/enveditor.py).
- 'EddyPro Bin Folder' is the directory that contains the eddypro executable file.
- 'EddyPro Project Template' is the template file for creating the executable eddypro project file. 
    - It can be found in the repository or can be other eddypro project file.
- 'EddyProj Project File' is the directory that the actual eddypro project file will be generated from template file.
- 'EddyPro Project ID' is the identifier for the project that can be decided by the user.
- 'EddyPro File Prototype' is the string that shows the format of the ghg file naming.
    - This can be obtained from the naming convention of ghg files.
- 'EddyPro Metadata File from GHG File' is the metadata file that can be found after unzipping a ghg file.
    - Unzipping any ghg file should be fine.
- 'EddyPro Dynamic Metadata' is a dynamic metadata file recorded from the field.
- 'EddyPro Output Path' is a directory path that the EddyPro run output will be saved.
- 'EddyPro Input GHG Path' is a directory path that contains all the input ghg files.

### Using the GUI
- The module can be run inside the pipeline, or the module process alone
- The command ```python pipeline.py``` launches a GUI that runs the whole pipeline or each individual module.
- In the GUI, the button 'Run EddyPro Application' will run only the module

### Using the EddyPro application
- The user can run EddyPro application manually by using outputs from ‘earlier’ parts of the pipeline, mainly outputs from [mastermetprocessor.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/master_met/mastermetprocessor.py) and [eddyproformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/eddypro/eddyproformat.md).
- The command ```python pipeline.py``` launches a GUI. In the GUI, the button 'Run EddyPro data preparation' calls the modules which generates the inputs required to run EddyPro software.
