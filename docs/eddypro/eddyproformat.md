# Documentation on eddyproformat process
This document is a code walkthrough on eddypro/eddyproformat.py process

## Overview
- The [eddyproformat](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/eddypro/eddyproformat.py) process creates the meteorological data for EddyPro input.
- The pipeline calls this process in [step#8](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md#8) of pre-pyfluxpro module, after the [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/master_met/mastermetprocessor.md) module. 

## Instructions to run

### Using the GUI
- There is an option to run this process independently. 
- This can be achieved using the [pipeline.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/pipeline.py) [GUI](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pipeline.md) and clicking the "Run" button in the "Run EddyPro data preparation" section.
- This runs the mastermetprocessor module and the eddyproformat process.

## Process
- eddyproformat process is executed within the [pre-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) module, after the mastermetprocessor module.
- The output is the meteorological data file formatted for EddyPro input.
- This formatted meteorological data file is generated from the output of the [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/master_met/mastermetprocessor.md) module.

### 1
- This process takes the output of mastermetprocessor module and soils key as input.
- The Soils key is an excel file which maps datalogger/meteorological variable names to Eddypro and Pyfluxpro variable names for the soil temperature and moisture variables for each site. A typical soils key file has the following columns :
  - Site name
  - Site ID
  - Instrument name
  - Datalogger/met water variable name
  - Datalogger/met temperature variable name
  - Pyfluxpro water variable name
  - Pyfluxpro temperature variable name
  - EddyPro water variable name
  - Eddypro temperature variable name
- The output is a meteorological data file formatted for EddyPro input.

### 2
- The input soil key is checked for expected format.
- The site name is extracted from the metadata file created in [mastermetprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/master_met/mastermetprocessor.md) step 3.
- Soil temperature and soil moisture variables of the particular site is extracted from the soils key.
- This contains the met tower variable names, EddyPro labels and PyFluxpro labels.

### 3
- Certain variable names are renamed to match Eddypro conventions. These variables are matched using regex pattern matching.
- o	In addition to more straightforward renamings such as RH_Avg' -> 'RH', variables with replicate measurements are given postscripts following [European Fluxes Database Cluster](http://www.europe-fluxdata.eu/home/guidelines/how-to-submit-data/general-information) conventions as per EddyPro conventions. 
- Soil temperature and moisture variables are renamed as per the Soils key.
- Rename AirTC_Avg, RTD_C_Avg to Ta_1_1_1 and Ta_1_1_2, where Ta_1_1_1 must be present. RTD being more accurate measurement, rename RTD_C_Avg to Ta_1_1_1 for eddypro. If not present, rename AirTC_Avg to Ta_1_1_1.
- Soil heat flux measurements shf_Avg(1) and shf_Avg(2) to be renamed as SHF_1_1_1 and SHF_2_1_1.
- Other variables that are renamed are : 'RH_Avg' -> 'RH', 'TargTempK_Avg'-> 'Tc', 'albedo_Avg'-> 'Rr', 'Rn_Avg'-> 'Rn', 'LWDnCo_Avg'-> 'LWin', 'LWUpCo_Avg'-> 'LWout', 'SWDn_Avg'-> 'SWin', 'SWUp_Avg'-> 'SWout', 'PARDown_Avg'-> 'PPFD', 'PARUp_Avg'-> 'PPFDr', 'Precip_IWS'-> 'P_rain', 'WindSpeed_Avg'-> 'MWS', 'WindDir_Avg'-> 'WD'.
- Units are formatted to match EddyPro formats. W/m^2'-> 'W+1m-2', 'Kelvin'-> 'K', 'm/s'-> 'm+1s-1', 'Deg'-> 'degrees', 'vwc'-> 'm+3m-3'

### 4
- All temperature measurements are changed from unit degree Celsius to Kelvin.
- Convert all NaNs to '-9999'. EddyPro recognizes '-9999' as invalid/empty data.

### 5
- Check if the list of required columns ['SWin', 'RH', 'LWin', 'PPFD'] are present.
- If any of the required columns are missing, log a warning message.

### 6
- At the end of execution, we have a meteorological data file formatted for eddypro. 
- The filename will be a concatenation between the MASTER_MET filename set in the .env and "_eddypro".
- This csv file is written to the same location specified by the user in settings(MASTER_MET).