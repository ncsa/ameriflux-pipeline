# Documentation on outputformat module
This document is a code walk-through on pyfluxpro/outputformat.py module

## Overview
- The [outputformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pyfluxpro/outputformat.py) process creates the csv file for Ameriflux submission.
- The module creates the csv file with the output from PyFluxPro software L2 run output(.nc file).
- The pipeline calls this process in post-pyfluxpro(https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/postpyfluxpro.md#2) module.

## Instructions to run
- This module is run after getting the results (graphs) from PyFluxPro software.
- Users can execute this module either using the GUI or the command line.
- Please see the [post_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/postpyfluxpro.md#instructions-to-run) documentation for further instructions. 

## Process

### 1
- The L2 run output (netCDF file) is read and validated for expected format.
- The QCFlag variables (variable names ending with '_QCFlag') are deleted. 
- Additional variables like ['latitude', 'longitude', 'crs', 'station_name', 'xldatetime', 'time', 'hour', 'second', 'minute', 'day', 'month', 'year', 'hdh', 'ddd',
'fsd_syn', 'solar_altitude', 'co2_sigma', 'h2o_sigma'] are also removed.

### 2
- The 'time' variable is renamed as 'TIMESTAMP_START' 
- A 'TIMESTAMP_END' variable is created with 'time' + 30min values.
- See [NOTES#16](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#16) for details.
- A warning message is logged if the timestamp columns do not span the entire year.

### 3
- Some additional variables are also renamed as per user settings in AMERIFLUX_VARIABLE_USER_CONFIRMATION and L1_AMERIFLUX_ERRORING_VARIABLES_KEY.
- For details, see [pre_pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#3) documentation.

### 4
- Crop site names are converted to Ameriflux site names.
- The crop site names are matched using regex.
- The current site names are : 
  - Miscanthus control: US-UiF
  - Maize Control: US-UiG
  - Miscanthus Basalt: US-UiB
  - Maize Basalt: US-UiC
  - Sorghum: US-UiE
- If a matching site name is not found, the sitename is kept as a blank space.
- The output filename will be 'US-Ui' + <ameriflux_site_name> + '_HH_' + <start_time> + '_' + <end_time>
- The csv file is written to the same directory as the L2 run output file.
