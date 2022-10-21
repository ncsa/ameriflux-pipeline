# Documentation on met processor module
This document will describe met_data_processor.py and the GUI metprocessor.py

## Overview
- The first step of the pipeline is to create a met data file that spans the required timeperiod.
- The module [met_data_processor.py](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/met_data_processor.py) is responsible for this task.
- Sometimes the data for the required timespan (typically a year) is scattered in multiple .dat files. These data need to be appended together to create continuous, yearlong data sets before being useable for analyses. 
- These .dat files, the start and end dates and the output file path are given as input to the met_data_processor module.
- met_data_processor processes each .dat files, sorts them by timestamp and concatenates the files to give one csv met data file spanning the entire timestamp.
- An optional user input is a key file. Some raw met tower variable names need to be changed to match variable naming standards used from 2021 onwards. This can be done by providing a key file containing the "Original" variable name and the "Target" variable name.
- The process creates a log file named "met_processor.log".

## Instructions to run

### Using GUI
- The command ```python metprocessor.py``` launches a GUI that is used to configure the settings and user inputs required to run the met_data_processor module.
- The GUI application is implemented using [tkinter](https://docs.python.org/3/library/tk.html) python library.
- Using the GUI, the user is able to browse through files, and choose various settings.
  - User can choose multiple files to process and merge. 
    - This is same as the "data" command line argument
  - User can choose the start and end date of the timespan of the processed and merged csv file. 
    - This is same as "start" and "end" command line arguments
  - User can choose the output location the processed file should be written to.
    - A csv file is expected.
    - This is same as "output" command line argument.
  - User also has the option to include a key file, if variable renaming is required. 
    - An excel (.xlsx) file with columns "Original" and "Target" is expected.
    - The "Original" column contains the variable names that are to be changed, and "Target" column contains the new variable names.
    - If the argument is present, the module reads the user input file and renames the variables present in "Original" column to their corresponding "Target" column values.
    - This is same as "key" command line argument.
- On clicking the "Generate" button, the met_data_processor.py module is called with the user settings and the output file is generated.

### Using command line
- To run using the default arguments, use command ```python met_data_processor.py```
- To get information on all command line parameters, please run ```python met_data_processor.py --help```
- If using the python command line, met_data_processor uses the following arguments
  - data : 
    - This argument takes in multiple filepaths that are comma separated. This will be read, processed and sorted by timestamp to generate a single csv file output.
    - This is a mandatory input field. If not specified, the code will ask for user inputs at runtime.
    - A typical user input for this parameter would be ```/Users/xx/data/master_met/input/FluxSB_EC.dat,/Users/xx/data/master_met/input/FluxSB_EC.dat.9.backup,/Users/xx/data/master_met/input/FluxSB_EC.dat.10.backup```
  - start :
    - This argument takes in the start date of the required timespan. This is an optional parameter
    - The date is given in yyyy-mm-dd format.
    - By default (if the parameter is not mentioned in the command), the start date is taken as the minimum timestamp of all the .dat input files.
    - A typical user input for this parameter would be yyyy-01-01
  - end :
    - This argument takes in the end date of the required timespan. This is an optional parameter
    - The date is given in yyyy-mm-dd format.
    - By default (if the parameter is not mentioned in the command), the end date is taken as the maximum timestamp of all the .dat input files.
    - A typical user input for this parameter would be yyyy-12-31
  - key :
    - This argument takes in an excel (.xlsx) file that maps the old met tower names to newer standardised names.
    - This is an optional argument.
    - By default (if the parameter is not mentioned in the command), variables are not renamed.
    - A typical user input for this parameter would be ```/Users/xx/data/master_met/input/metprocessor_key.xlsx```. 
    - This key file is expected to contain two columns named "Original" and "Target". The "Original" column contains the variable names that are to be changed, and "Target" column contains the new variable names.
    - If the argument is present, the module reads the user input file and renames the variables present in "Original" column to their corresponding "Target" column values.
  - output :
    - This argument takes in the full output path of a csv file to which the processed and merged .dat files will be written.
    - By default (if the parameter is not mentioned in the command), the processed and merged data will be written to ```/Users/xx/data/master_met/input/Flux.csv```.
- A typical run command with all arguments:
```python met_data_processor.py --data /Users/xx/data/master_met/input/FluxSB_EC.dat,/Users/xx/data/master_met/input/FluxSB_EC.dat.9.backup,/Users/xx/data/master_met/input/FluxSB_EC.dat.10.backup --start 2021-01-01 --end 2021-12-31 --key /Users/xx/data/master_met/input/metprocessor_key.xlsx --output /Users/xx/data/master_met/input/Flux.csv```

## Process
- met_data_processor module is usually the first step in the pipeline. 
- This creates a single meteorological data csv file that spans the required timeframe. 
- All logs are captured in met_processor.log file.

### 1
- The first step is to validate all user inputs to this module. 
- This includes the multiple files (in the ```data``` argument), start and end dates (```start``` and ```end``` arguments), output file path (```output``` argument) and key file (```key``` argument).
- Validations are performed by ```validate_inputs()```  and ```DataValidation.is_valid_met_key()``` method.
- Validations include :
  - Check if the input files exists.
  - Check if the start and end dates are valid.
  - Check if the directory path for the output file exists
  - Check if the output file is a csv
  - Check if the key file is an excel (.xlsx) file and the format is as expected, if present in argument.
- If any of the above validations fail, it returns an error and the process is aborted.

### 2
- The module reads each input files (typically .dat/csv files) given in the ```data``` argument and process each file.
- The separate .dat files are converted to separate csv files without any processing. These csv files are written to the same location as each input file. 
- The files are read in a robust manner with separators of comma, semicolon and tab.
- If files can't be read, an error is logged and the process is aborted.

### 3
- On reading each input file, the first line of each file is taken as the file meta data. This contains the site name and is stored for future use.
- The next three rows are taken as the meta data and stored in a separate dataframe for future use.
- Validations are done for the meta data. Validations include :
  - Check if 'TIMESTAMP' column is present (first row).
  - Check if 'TS' is present in the units row (second row).
  - Check if 'Min' or 'Avg' is present in the third row.
- If any of the above validations fail, it returns an error and the process is aborted.
- The rest of the data is read and stored in another dataframe.

### 4
- As mentioned in NOTES #24, some variables can be renamed in the met process.
- The variables in the key file (```key``` argument) and variables mentioned in the NOTES #24 are renamed.
  - Checks are done to make sure that the renaming is done correctly and the column names are unique.

### 5 
- For each input file, the process stores
  - met data, 
  - the file meta data (first row), 
  - the site name extracted from the file meta data, 
  - the meta data (second, third and fourth row)

### 6
- If the site name extracted from different input files are different, an error message is logged, as data merge for different sites is not recommended.
- The process is aborted.

### 7
- All the met data from different files are concatenated.
- Empty spaces are replaced with 'NAN'.

### 8
- The timestamp column of the met data is converted to python-readable datetime format.
- The met data is sorted by timestamp (ascending).
- If there is an input start date, the met data starts from +30 minutes from the input start date.
- If there is an input end date, the met data ends at 00:00 for the next day from the input end date.
- For example, if start date is "2021-01-01" and end date is "2021-12-31", met data will span the time from "2021-01-01 00:30" to 2022-01-01 00:00".
- If input start and end dates are not present, the met data will span the entire timeframe present in the input files.

### 9
- The met data and meta data are merged.
- A validation check on the column names is done before merge. If validation fails, an error message is logged and process aborted.

### 10
- The processed and merged data is written to the output location mentioned in ```output``` argument.