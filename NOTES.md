# Notes
- All notable decisions and code structure is documented in this file.
- Each decision made will be tagged and the tag will be present in the corresponding code section.

## Notes on data and decisions made
### 1 
- The met data file is a csv file that contains met tower variable data and some meta data. The first row of the file contains file level meta data, where the most useful is the site name.
- Site name can be Maize-Basalt / Maize (ZMB), Maize-Control / Maize-No-Basalt (ZMC), Miscanthus-Basalt / Miscanthus (MGB), Miscanthus-Control /Miscanthus-No-Basalt (MGC) and Sorghum (SB).
- The second row contains the met tower variables and the third row contains their unit of measurement.
- The fourth row of met data file contains either 'Min' or 'Avg' values for each variable, which mentions if the measurement recorded is the minimum or average of the 30min timeframe.
- We use the variable names and the measurement data starting from fifth line onwards as the dataframe (df) and treat the first 3 rows as the meta data (file_df_meta). 
### 2
- Separate out the dataframe meta data, including the met tower variable names and units into another dataframe (df_meta). 
- When new variables are added to the dataframe (df), add the variable names and unit of measurement to the meta dataframe (df_meta). This is used for joining the two dataframe at the end. 
### 3
- The site name obtained in the meta data (file_meta) is used to match with the soils key. 
- Soils key is an excel sheet which gives the mapping of met tower soil temperature and moisture variable names to eddypro labels.
### 4
- U_Avg and V_Avg are missing units in the input met data. The cells for the units are empty in the input met file. Add units to these variables in df_meta.
### 5
- Raw precip data is to be present for every 5 min and the valid range is between 0-0.2 inches. If a timestamp is missing, insert the timestamp with a fill value of NAN. If the precip data is not within the valid range limit, replace the value with NAN.
- When aggregating the 5min data to 30min, if there is an NAN in any of the 5min timestamps, put the aggregated value of the 30min timestamp to be NAN as well. 
### 6
- Some new variables are required for processing and formatting of met data. These are kept track in a new_variable list and deleted at the end.
- This will ensure only met tower variables are pushed to EddyPro.
### 7
- EddyPro does not handle missing timestamps. If there are missing timestamps in the met data, insert missing timestamps with fill value.
- If there is a large gap in the timestamps in met data, user can choose whether or not to insert missing timestamps.
### 8
- The met data and precip data are merged on the timestamp column. 
- If there are extra timestamps in met data, keep them in the final dataframe while filling the precip data as NANs.
- If there are extra timestamps in precip data, ignore that.
