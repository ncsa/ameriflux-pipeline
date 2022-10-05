#Automation workflow
##Project :
Code is structured so that input data files and output data files are in one directory.Follow Readme for instructions.
##Manual steps :
* 1.  The FLUX.data.backup file has first row detailing the file meta data, second row the variable names, third row as abbreviation of variable names, and fourth row the units.
Will be working with the variable names and data only.a.
Store meta data in another meta data file and delete the rows.
Filename FLUXSB_EC.dat.meta.csvb.
In the meta datafile, only the variable names and units are required.
Delete first and 4th row.
* 2.  Store the file as csv in the /data folder(Step 1 in guide)
##Automation :
* 1.  Sync time :The flux data timestamp should be adjusted to 30min behind. (Step 2 in guide). Shifting a cell up in the timestamp column is not ideal.Solution : convert string timestamp to python datetime object. Shift 30min via datetime functionality.
* 2.  Missing timestamps: (Step 3 in guide)Solution : get timedelta between two timestamps. If the timedelta is more than 30min, there is a missing timestamp. The number of rows to be inserted is given by (timedelta)/30. Insert blank rows at the row indexes that return timedelta>30. When inserting the blank rows, populate the timestamp column with generated timestamp intervals of 30min. This is done using time interval functionality given the endtimestamp and starting timestamp.
* 3.  User confirmation required if large missing timestamps Solution : the threshold is set as 96(2 days) as default. If number of rows to be inserted is more than 96, user confirmation is requested. If user enters Y, insert the rows. If user inputs N, the dataframe till now is written to the output filepath specified.
* 4.  Changed timestamp format to reflect that needed for EddyPro : changed timestamp format to str
* 5.  Calculation of soil heat flux required only for earlier years (step 5 in guide)Checks if the column shg_mV_Avg exists. If yes, do the procedure. If not skip.
(Need clarification on column names)
* 6.  Calculation of Absolute humidity (Step 6 in guide)Checked the code in ofTools VBA. Implemented the same in python.(Need clarification on formula)
* 7.  Populate blank cells with ‘NAN (Step 4) :Solution : python replace functionality. Replace ‘’ with ‘NAN’. Also replace NaN with ‘NAN’.
* 8.  Delete newly created columns/variables :Newly created columns are deleted.
* 9.  Insert units as first row of processed dataframe :The meta data is stored in file FLUXSB_EC.dat.meta.csv. Read the file as a csv. Check if the number of columns in the processed df and the read meta_df is the same. If yes, insert the units from meta_df as the first row of the final df.
* 10.Write the processed df to output path specified.