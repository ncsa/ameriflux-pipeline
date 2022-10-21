# Documentation on mastermetprocessor module
This document is a code walkthrough on master_met/mastermetprocessor.py module

## Overview
- The [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/master_met/mastermetprocessor.py) module creates the master meteorological data.
- The pipeline calls this process in [step#8](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#8) of pre-pyfluxpro module.

## Instructions to run

### Using the GUI
- There is an option to run this module independently. 
- This can be achieved using the [pipeline.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pipeline.py) GUI and clicking the "Run" button in the "Run EddyPro data preparation" section.

## Process
- mastermetprocessor module is typically the first module executed within the [pre-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) module.
- The output of this module is the master meteorological data file.
- This master meteorological data file is generated from the output of the [metprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/metprocessor.md) module.

### 1
- Inputs required by this module are :
  - Meteorological data file - A csv file with meteorological data. This is typically the output from metprocessor module
  - Precipitation data file - Excel file with precipitation data for the site in inches.
  - Missing timestamps threshold - The number of 30min missing timestamps that acts as a threshold when inserting missing timestamps. This is used in both inserting missing timestamps for both precipitation data and meteorological data.
  - User confirmation on inserting timestamps - A confirmation from the user whether to automatically insert missing timestamps greater than the 'Missing timestamps threshold'
- These inputs can be set from the [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md)

### 2
- The input meteorological csv file is read and the met data and metadata is separated out. See [NOTES #1](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#1).
- The number of variables and data records are logged for information.

### 3
- Metadata is further separated out into file metadata and metadata of the flux variables. See [NOTES #2](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#2).
- Metadata is validated to check if it meets the expected format.

### 4
- Units are added for U_Avg and V_Avg variables. See [NOTES #4](https://github.com/ncsa/ameriflux-pipeline/blob/develop/NOTES.md#4).

### 5
- Input precipitation data file is read and checked if it meets the expected format.
- The data is checked to see if there are any missing timestamps and if the data is within the expected range.
- User can change the expected range and timeperiod as mentioned in the [config](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/config.md) module.
- The timeperiod for each record in precipitation data is currently set as 5min and that of meteorological data is set as 30min. 
- The expected range is currently set to be between 0 inches and 0.2 inches.
- If there are missing timestamps, the missing timestamps are inserted as long as the missing timespan is less than the 'Missing timestamps threshold' user input.
- If the missing timespans greater than the threshold, process continues as per "User confirmation on inserting timestamps" input.
  - If the user confirmation is "Y/Yes", the code inserts the missing timestamps.
  - If user confirmation is "N/No", the code ignores the missing timestamps and proceeds to the next step.
  - If user confirmation is "A/Ask", the code asks during runtime whether or not to insert the missing timestamps.

