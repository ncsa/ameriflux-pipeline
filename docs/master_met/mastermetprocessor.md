# Documentation on mastermetprocessor module
This document is a code walkthrough on master_met/mastermetprocessor.py module

## Overview
- The [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/master_met/mastermetprocessor.py) module creates the master meteorological data.
- The pipeline calls this process in [step#8](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#8) of pre-pyfluxpro module.

## Instructions to run

### Using the GUI
- There is an option to run this module independently. 
- This can be achieved using the [pipeline.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pipeline.py) GUI and clicking the "Run" button in the "Run EddyPro data preparation" section.
- This runs the mastermetprocessor and the eddyproformat modules.

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
- The expected range is currently set to be between 0 inches and 0.2 inches. Anything outside this the range is changed to 'NAN'.
- The timeperiod for each record in precipitation data is currently set as 5min.

### 6
- If there are missing timestamps, the missing timestamps are inserted as long as the missing timespan is less than the 'Missing timestamps threshold' user input.
- If the missing timespans greater than the threshold, process continues as per "User confirmation on inserting timestamps" input.
  - If the user confirmation is "Y/Yes", the code inserts the missing timestamps.
  - If user confirmation is "N/No", the code ignores the missing timestamps and proceeds to the next step.
  - If user confirmation is "A/Ask", the code asks during runtime whether to insert the missing timestamps.

### 7
- Convert precipitation in inches to millimeter. The unit is 'mm'.
- The precipitation data is resampled to 30min time periods.

### 8
- Check for missing timestamps for meteorological data and proceed as mentioned in step 6.
- User can change the timeperiod as mentioned in the [config](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/config.md) module.
- The timeperiod for each record in meteorological data is currently set as 30 min.

### 9
- Sync time for the meteorological data.
- Campbell Datalogger timestamps refer to the end of a 30-minute period, while Li-COR IRGA timestamps refer to the start of each 30-minute period. 
- To account for this, remove the first timestamp of the year (i.e. yyyy/01/01 00:00), and append the first 30-minute period from the succeeding year’s meteorological data to the current year’s sheet. 
- We will shift all meteorological timestamps back 30 minutes to match the IRGA timestamp.
- The meteorological data is resampled to 30min time periods.

### 10
- Calculation of soil heat flux is done, if the variables are not present in the meteorological data.
- Regex pattern matching is done for shf_Avg(1) and shf_Avg(2). If the variables are not present, the soil heat flux is calculated.
- Soil heat flux is calculated from shf_mV and shf_cal variables. Calculated as (shf_mV * shf_cal).

### 11
- Calculation of absolute humidity is done using variables AirTC_Avg and RH_Avg.
- Regex pattern matching is done to check if columns AirTC_Avg and RH_Avg exists in meteorological data.
- Ah_fromRH is calculated as :
  - T (float): Air temperature in celsius. AirTC_Avg column from meteorological data.
  - RH (float): Relative humidity in percentage. RH_Avg column from meteorological data.
  - VPsat = 0.6106 * (17.27 * T / (T + 237.3))
  - vp = RH * VPsat / 100
  - Rv = 461.5  # constant : gas constant for water vapour, J/kg/K
  - AhFromRH = 1000000 * vp / ((T + 273.15) * Rv)
- The unit for Ah_fromRH is 'g/m^3'.
- If the calculation fails, a warning is logged.

### 12
- Calculation of shortwave out and albedo is as follows :
- SW_out_Avg = Shortwave In - Net Shortwave = CM3Dn_Avg = SWUp_Avg
- Albedo_Avg = Shortwave Out / Shortwave In = CM3Dn_Avg / CM3Up_Avg = SWUp_Avg / SWDn_Avg = albedo_avg
- If albedo is already in the dataset, the calculation is not done in the code.
- The dataset will contain either the SWUp/Dn measurements of the CM3UP/Dn measurements, and never both.
- Regex pattern matching is done to check for SW instruments and CM3 instruments.
- Unit for SW_out_Avg and ALB is 'W/m^2'.

### 13
- All empty cells / data points are filled with 'NAN'.

### 14
- If the precipitation data is formatted successfully, the precipitation data is merged with meteorological data on the 'TIMESTAMP' column.
- If there are extra timestamps in the meteorological data, the additional records are created in the precipitation data to match meteorological data and filled with 'NAN'.

### 15
- At the end of this module execution, we have a master meteorological data written to the location specified by the user in settings(MASTER_MET).
- The file metadata(mentioned in step 3) is also written to the same location as another csv file.