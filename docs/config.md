# Documentation on config module
This document will describe the config.py module

## Overview
- This module reads all user settings and configures the python modules to process according to these user inputs.
- The user inputs are read from the env file that is generated with [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) module.
- If some required configurations are not provided by the user, this module sets a default value.
- This module also adds additional configurations that are not user-defined.
  - QC_PRECIP_LOWER gives the precipitation lower threshold value in inches. This is set as 0.0
  - QC_PRECIP_UPPER gives the precipitation upper threshold value in inches. This is set as 0.2
- Users can change the configuration settings by modifying the [config](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/config.py) module.
- The default values can be changed by modifying the second parameter in ```os.getenv()``` function for the corresponding settings.