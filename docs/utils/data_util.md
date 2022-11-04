# Documentation on datautil module
This document is a code walk-through on data_util.py module

## Overview
- The [data_util](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/utils/data_util.py) is a utility module that supports various data functionalities.
- This module is used throughout the pipeline at various stages.
- This is not a standalone module and does not produce any output files.

## Process
- The [data_util](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/utils/data_util.py) module ensures that pipeline runs smoothly.
- The module contains multiple methods for various data functions.
- The functionalities of this module is explained below.

### 1
- All read and write operations are performed by this module

### 2
- Extracting site name from meteorological data.

### 3
- Getting the directory name from a path

### 4
- Converting a string to a valid datetime format

### 5
- Getting the OS platform running in local machine

### 6
- Creating common file names