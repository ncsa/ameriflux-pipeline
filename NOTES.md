# Notes
- All notable decisions and code structure is documented in this file.
- Each decision made will be numbered and the tag will be present in the corresponding code section.

## Notes on data and decisions made
### 1 
- The met data file is a csv file that contains met tower variable data and some metadata. The first row of the file contains file level metadata, where the most useful is the site name.
- Site name can be Maize-Basalt / Maize (ZMB), Maize-Control / Maize-No-Basalt (ZMC), Miscanthus-Basalt / Miscanthus (MGB), Miscanthus-Control /Miscanthus-No-Basalt (MGC) and Sorghum (SB).
- The second row contains the met tower variables and the third row contains their unit of measurement.
- The fourth row of met data file contains either 'Min' or 'Avg' values for each variable, which mentions if the measurement recorded is the minimum or average of the 30min timeframe.
- We use the variable names and the measurement data starting from fifth line onwards as the dataframe (df) and treat the first 3 rows as the meta data (file_df_meta). 
### 2
- Separate out the dataframe metadata, including the met tower variable names and units into another dataframe (df_meta). 
- When new variables are added to the dataframe (df), add the variable names and unit of measurement to the meta dataframe (df_meta). This is used for joining the two dataframe at the end. 
### 3
- The site name obtained in the meta data (file_meta) is used to match with the soils key. 
- Soils key is an excel sheet which gives the mapping of met tower soil temperature and moisture variable names to eddypro labels.
### 4
- U_Avg and V_Avg are missing units in the input met data. The cells for the units are empty in the input met file. Add 'm/s' units to these variables in df_meta.
### 5
- Raw precip data is to be present for every 5 min and the valid range is between 0-0.2 inches. If a timestamp is missing, insert the timestamp with a fill value of NAN. If the precip data is not within the valid range limit, replace the value with NAN.
- The precipitation data with 5min timestamps are resampled to 30min timestamps. 00-30 is summed and stored in 00min (beginning of timestamp).
- When aggregating the 5min data to 30min, if there is an NAN in any of the 5min timestamps, put the aggregated value of the 30min timestamp to be NAN as well. 
### 6
- Some new variables are required for processing and formatting of met data. These are kept track in a new_variable list and deleted at the end.
- This will ensure only met tower variables are pushed to EddyPro.
### 7
- EddyPro does not handle missing timestamps. If there are missing timestamps in the met data, insert missing timestamps with fill value.
- If there is a large gap in the timestamps in met data, user can choose whether or not to insert missing timestamps.
### 8
- The met data and precip data are merged on the timestamp column. Merging is done on the time delayed timestamp column of met data.
- If there are extra timestamps in met data, keep them in the final dataframe while filling the precip data as NANs.
- If there are extra timestamps in precip data, ignore that.
### 9
- If there is a large gap in timestamps in either met data or precip data, ask for user confirmation to insert the missing timestamps or ignore.
### 10
- Calculation of shortwave out and albedo is as follows :
- SW_out_Avg = Shortwave In - Net Shortwave = CM3Dn_Avg = SWUp_Avg
- Albedo_Avg = Shortwave Out / Shortwave In = CM3Dn_Avg / CM3Up_Avg = SWUp_Avg / SWDn_Avg = albedo_avg
- If albedo is already in the dataset, the calculation is not done in the code.
- The dataset will contain either the SWUp/Dn measurements of the CM3Up/Dn measurements, and never both.
### 11
- In Soils key, the EddyPro labels are the same as those used for PyFluxPro L1 and L2 control file variables to meet AmeriFlux standards.
- PyFluxPro formatting to AmeriFlux standards uses two L1.txt files. 
- One is mainstem L1 and other L1 will contain only the variables that are not present in mainstem but is needed for Ameriflux. These will be named Ameriflux_Only.
- There will not be duplicate variables ie. there will not be variables that are present in both these files.
### 12
- PyFluxPro does not recognise the unit for SH variable. The unit for SH variable has been changed to 'kg/kg'. 
- This is updated in the Ameriflux-Mainstem Key excel sheet under the 'Units after formatting' column.
- If original unit is to be kept, remove 'kg/kg' from the cell.
### 13
- For Ameriflux-friendly L1 and L2, we only write Ameriflux friendly variables which are listed out in the Ameriflux-Mainstem-Key.xlsx.
### 14
- For Ameriflux-friendly L2, H2O_SIGMA is used as DependencyCheck source instead of H2O_IRGA_Vr
### 15
- For Soil water content variables in Ameriflux-friendly L2, range checks should be multiplied by 100 as these are in percentages.
### 16
- TIMESTAMP_START and TIMESTAMP_END column is created from time column from netCDF PyFluxPro output and inserted at indexes 0 and 1 respectively. 
- The TIMESTAMP_START column corresponds with TIMESTAMP column from PyFluxPro L2 output file.
### 17 
- Pipeline is split into two phases, one to be run before PyFluxPro(pre_pyfluxpro) and one after PyFluxPro(post_pyfluxpro).
- The first phase generates L1 and L2 control files that meet Ameriflux standards.
- User then runs the PyFluxPro 3.3.2 manually and use the generated L1 and L2 control files. Once user has the netCDF output for L2 run, user proceeds to second stage of the pipeline.
- The second phase generates the csv file named US-Ui<site_name>\_HH\_<timestamp_start>_<timestamp_end>.csv that meets Ameriflux standards.
### 18
- netCDF4 python library is supported only in Python version 3.8. This pipeline has a strict requirement of Python 3.8
### 19
- During merge of dat files / raw met files from the server, the end date is taken as the next day midnight and start date is taken as 30min forward.
- The start time will be 00:30 and the end time will be 00:00 of the next day. 
- Campbell data logger timestamps refer to the end of a 30-minute period.
- The timestamps are shifted 30min behind in the mastermet processing, to reflect the starting time of the 30min period. This way the master met output will have timestamps from 00:00 to 23:30.
### 20
- In 2021 there has been a program change resulting in the change of some datalogger met variables names. Hence when merging the met data, certain old variables names are to be changed to newer standardized variable names.
- These name changes are implemented in code { 'cnr<num>_T_C_Avg' -> 'CNRTC_Avg', 'cnr<num>_T_K_Avg' -> 'CNRTK_Avg', 'VWC_' -> 'VWC1_', 'TC_' -> 'TC1_'}
- These name changes can be included in Ameriflux-Mainstem-Key.xlsx file { 'CM3Up_Avg'-> 'SWDn_Avg', 'CM3Dn_Avg'-> 'SWUp_Avg', Solar_Wm2_Avg -> SWDn_Avg, Sw_Out_Avg -> SWUp_Avg, 'CG3UpCo_Avg'-> 'LWDnCo_Avg', 'CG3DnCo_Avg'-> 'LWUpCo_Avg', 'NetTot_Avg'-> 'Rn_Avg', Net_Rad_Avg -> Rn_Avg }
### 21
- In L2.txt, the RangeCheck should have lower and upper. 
- The lower and upper have comma separated items. The number of items can be 1 or 12.
### 22
- When generating pyfluxpro input excel file, the TIMESTAMP column of the full_output sheet is shifted 30min behind.
- This is because the 'time' column from EddyPro full output reflects the ending of the 30min interval. The met_data_30 sheet TIMESTAMP column reflects the starting of the 30min interval.
- Hence the TIMESTAMP column of the full_output sheet is shifted 30min behind to get the correct timestamp, which reflects the starting of the 30min interval.
### 23
- In pyfluxpro input excel sheet for ameriflux, Albedo values are to be converted to percentage values. Desirable albedo values are between 0 and 1. Values outside of this range are converted to NaNs.
### 24
- Some met tower variable names are to be changed in the metmerger phase. Eg: { 'CM3Up_Avg'-> 'SWDn_Avg', 'CM3Dn_Avg'-> 'SWUp_Avg', Solar_Wm2_Avg -> SWDn_Avg, Sw_Out_Avg -> SWUp_Avg, 'CG3UpCo_Avg'-> 'LWDnCo_Avg', 'CG3DnCo_Avg'-> 'LWUpCo_Avg', 'NetTot_Avg'-> 'Rn_Avg', Net_Rad_Avg -> Rn_Avg }
- These should be done in met merger as for some years, both the variable names can be present in a whole year run.
### 25
- Ameriflux site names for all sites are as follows
- Miscanthus control: US-UiF , Maize Control: US-UiG , Miscanthus Basalt: US-UiB , Maize Basalt: US-UiC , Sorghum: US-UiE, Switchgrass: US-UiA

