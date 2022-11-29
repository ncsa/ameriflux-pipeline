# Documentation on enveditor
This document will describe the GUI enveditor application.

## Overview 
- The ameriflux_pipeline module uses several user inputs and settings to run. 
- The command ```python enveditor.py``` launches a GUI that is used to configure the settings and user inputs required to run the pipeline.
- The GUI application is implemented using [tkinter](https://docs.python.org/3/library/tk.html) python library.
- Using the GUI, the user is able to browse through files, choose and type in various settings.
- An "Info" button is provided which gives a brief description of the setting.
- On clicking the "Save" button, a .env file is generated in the working directory.
- This .env file is used by the pipeline ([pre_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) and [post_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/postpyfluxpro.md) modules) to read in the user settings and run the pipeline accordingly.

## Configuration Details
- There are several groups of variables in the editor
1. Sync files from the server
  - allows the user to sync the ghg files and met files 
  - need to provide server url and auth information, such as username and password
  - need to set up the file path from the server and local machine
  - only runs when the confirmation is set to 'Y'
  - [Sync module](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/utils/syncdata.md) is skipped by default.
  - If the Sync module needs to be run, the user inputs can be configured by setting SHOW_DATA_SYNC to be True in [enveditor.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/enveditor.py#L29)
  - The env variables selected for this section are as described [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/utils/syncdata.md#using-gui). :
2. Variables for master met and eddypro formatting
  - files and variables needed for creating master meteorological data and for formatting the eddypro inputs
  - The env variables selected for this section are :
    - INPUT_MET : meteorological data file (csv) that spans the desired time period in 30min increments
    - INPUT_PRECIP : precipitation data file (excel) that spans the desired time period in 5min increments.
    - MISSING_TIME_USER_CONFIRMATION : A confirmation from the user whether to automatically insert or ignore or ask in case of missing timestamps
    - MISSING_TIME : The number of 30min missing timestamps the user is willing to tolerate in the data.
    - MASTER_MET : Full file path to write the master meteorological csv file
    - INPUT_SOIL_KEY : excel file which maps datalogger/meteorological variable names to Eddypro and Pyfluxpro variable names for the soil temperature and moisture variables for each site.
    - See [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/master_met/mastermetprocessor.md) and [eddyproformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/eddypro/eddyproformat.md) for details.
3. Variables for running EddyPro
    - files and parameters needed for running the EddyPro software in a headless manner.
    - The env variables selected for this section are as described [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/eddypro/runeddypro.md#set-parameters).
      - Of the env variables, the EddyPro output path should be an empty directory. See Pre-pyfluxpro module [step#9](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#9) for details.
4. Variables for PyFluxPro input sheet
    - files and parameters needed for creating Pyfluxpro input excel sheet
    - The env variables selected for this section are :
      - FULL_OUTPUT_PYFLUXPRO : filename for the formatted eddypro full_output sheet
      - MET_DATA_30_PYFLUXPRO : filename for master meteorological data file
      - PYFLUXPRO_INPUT_SHEET : filename for pyfluxpro input excel sheet
      - PYFLUXPRO_INPUT_AMERIFLUX : filename for pyfluxpro input excel sheet formatted for Ameriflux
      - See [pyfluxproformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/pyfluxproformat.md), [amerifluxformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/amerifluxformat.md) for details
5. Variables for PyFluxPro control files
    - files and parameters needed for creating Pyfluxpro L1 and L2 control files
    - The env variables selected for this section are :
      - L1_MAINSTEM_INPUT : Pyfluxpro template L1 control file used for mainstem processing.
      - L1_AMERIFLUX_ONLY_INPUT : Pyfluxpro template L1 control file containing ameriflux-only variables
      - L1_AMERIFLUX_MAINSTEM_KEY : excel file that the user can use to select which variables to write in the output L1 file.
      - L1_AMERIFLUX_RUN_OUTPUT : filepath (.nc) where the pyfluxpro L1 run output should be written.
      - L1_AMERIFLUX : filepath where the output L1 should be written
      - AMERIFLUX_VARIABLE_USER_CONFIRMATION : user confirmation to use Ameriflux variable names. See [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#3) for details.
      - L1_AMERIFLUX_ERRORING_VARIABLES_KEY : key for mapping some variables names not recognized by Pyfluxpro software. See [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#3) for details.
      - L2_MAINSTEM_INPUT : Template L2 control file used for mainstem processing.
      - L2_AMERIFLUX_ONLY_INPUT : template L2 control file containing ameriflux-only variables
      - L2_AMERIFLUX_RUN_OUTPUT : filepath (.nc) where the pyfluxpro L2 run output should be written.
      - L2_AMERIFLUX : filepath where the output L2 should be written.
      - See pre-pyfluxpro [step#14](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#14) and [step#15](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#15) for details

