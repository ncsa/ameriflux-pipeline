# Documentation on input validation module
This document is a code walk-through on input_validation.py module

## Overview
- The [input_validation](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/utils/input_validation.py) module is a utility function that supports various input validations.
- This module is used throughout the pipeline at various stages.
- This is not a standalone module and does not produce any output files.

## Process
- The [input_validation](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/utils/input_validation.py) module ensures that the user inputs / settings are valid.
- The module contains multiple methods for input and data validations.
- The functionalities of this module is explained below.

### 1
- Server_sync method validates all user settings related to the [Sync](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/utils/syncdata.md) module.

### 2
- Master_met method validates all user settings related to the [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/master_met/mastermetprocessor.md#1) module.
- Master_met_eddypro method checks if the Soils-key meets expected format. 

### 3
- Eddypro_headless method validates all user settings related to [runeddypro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/eddypro/runeddypro.md#set-parameters) module.

### 4
- Pyfluxpro method validates all user settings for generating pyfluxpro input excel sheet. See [pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/pyfluxproformat.md) module for details.

### 5
- l1format method validates all user settings for generating L1 control file for EPL-type processing. See [pre_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/pyfluxproformat.md#14) and [l1format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l1format.md) for details.

### 6
- l2format method validates all user settings for generating L2 control file for EPL-type processing. See [pre_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/pyfluxproformat.md#15) and [l2format](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pyfluxpro/l2format.md) for details.
