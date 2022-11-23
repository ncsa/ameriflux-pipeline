# Documentation on config module
This document will describe the config.py module

## Overview
- This module reads all user settings and configures the python modules to process according to these user inputs.
- The user inputs are read from the env file that is generated with [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) module.
- If some required configurations are not provided by the user, this module sets a default value.
- This module also adds additional configurations that are not user-defined.
  - QC_PRECIP_LOWER gives the precipitation lower threshold value in inches. This is set as 0.0
  - QC_PRECIP_UPPER gives the precipitation upper threshold value in inches. This is set as 0.2
    - User can modify these settings [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/config.py#L132).
  - MET_TIMEPERIOD gives the timeperiod (in minutes) of one record in meteorological data file. This is set as 30.0
  - PRECIP_TIMEPERIOD gives the timeperiod (in minutes) of one record in percipitation data file. This is set as 5.0.
    - User can modify these settings [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/config.py#L137).
  - PYFLUXPRO_OVERLAP_TIMESTAMP flag checks if eddypro fulloutput sheet and metdata sheet in pyfluxpro_input.xlsx sheet need to have overlapping timestamps.
    - If set to true, eddypro fulloutput sheet and metdata sheet needs to have overlapping timestamps. If not, the pyfluxpro data processing will be aborted.
    - If set to False, the check for overlapping timestamp will not be executed.
    - User can modify these settings [here](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/config.py#L142).
- Users can change the configuration settings by modifying the [config](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/config.py) module.
- The default values can be changed by modifying the second parameter in ```os.getenv()``` function for the corresponding settings.
