# AmeriFlux-pipeline

**AmeriFlux-pipeline** is an automated process of handling flux data for AmeriFlux submission.
This automated code creates master met data, runs EddyPro automatically and creates input sheet for PyfluxPro input.

## Prerequisites

### Requirements
- Python 3.8
- EddyPro 7.0.6 (https://www.licor.com/env/support/EddyPro/software.html) exec files
- PyFluxPro 3.3.2 (https://github.com/OzFlux/PyFluxPro)

## Files :
- master_met / mastermetprocessor.py creates the master met data file
- eddypro / eddyproformat.py creates master met data formatted for eddypro headless run
- eddypro / runeddypro.py is responsible for the eddypro headless run
- pyfluxpro / pyfluxproformat.py creates the input excel sheet for pyfluxpro
- pyfluxpro / amerifluxformat.py creates the input excel sheet for pyfluxpro as per Ameriflux standards
- pyfluxpro / l1format.py creates L1 control file as per Ameriflux standards
- pyfluxpro / l2format.py creates L2 control file as per Ameriflux standards
- pyfluxpro / outputformat.py creates csv file with data formatted for Ameriflux submission from the L2 run output
- utils / syncdata.py performs syncing of GHG data with server and local
- utils / data_util.py performs various data operations
- utils / input_validation.py performs validations on user inputs from the env file
- utils / process_validation.py performs validations on data
- templates/ folder keeps the eddypro project files needed to run EddyPro headless
- enveditor.py is the GUI for helping the users to set the input and output data
- config.py lists all configurations
- requirements.txt lists the required packages
- met_data_merge.py merges multiple .dat files containing raw met data to a csv file that can then be used in the pipeline.
- pre_pyfluxpro.py runs all processing steps till PyFluxPro runs. It generates L1 and L2 control files as per Ameriflux standards
- post_pyfluxpro.py runs all post processing steps to convert the L2 run output to csv file required for Ameriflux submission.

## Installation

1. Clone the GitHub repository
```
git clone https://github.com/ncsa/ameriflux-pipeline.git
```

2. Change working directory
```
cd ameriflux-pipeline
```

3. Set up python virtual environment
- Python virtualenv package should be installed in the machine
- (Linux or MAC):
```
virtualenv -p python3.8 venv
source venv/bin/activate
```
- (Windows):
```
python -m venv env
.\env\Scripts\activate
```
- Or if you prefer to use conda,
```
conda create --prefix=venv python=3.8
conda activate venv
```
4. Install dependencies:
- The model is tested on Python 3.8, with dependencies listed in requirements.txt.
- To install these Python dependencies, please run following command in your virtual env
```
pip install -r requirements.txt
```
<<<<<<< HEAD
- Or if you prefer to use conda,
```
conda install --file requirements.txt
```
5. If multiple dat files for met data needs to be merged, run ```python met_data_merge.py```. 
=======
5. If multiple dat files needs to be merged, run ```python met_data_merge.py```. 
>>>>>>> 57cd9552cca8a5e0135886bf0a26276f7e593a55
- To request all command line parameters, please run ```python met_data_merge.py --help``` 
- data parameter takes in comma separated file paths. This is a mandatory field. If not specified, the code will ask for user inputs at run time.
- start parameter takes in the start date for merger, given in yyyy-mm-dd format. This will later be expanded to support any plausible date formats. If not given, by default it takes in 2021-01-01
- end parameter takes in the end date for merger, given in yyyy-mm-dd format. This will later be expanded to support any plausible date formats. If not given, by default it takes in 2021-12-31
- output parameter takes in the full output path of a csv file which will write the merged output to. By default it will write to master_met/input/Flux.csv
- To run the python module with default parameters run ```python met_data_merge.py```
- Run command example with all arguments:  
``` python met_data_merge.py --data /Users/xx/data/master_met/input/FluxSB_EC.dat,/Users/xx/data/master_met/input/FluxSB_EC.dat.9.backup,/Users/xx/data/master_met/input/FluxSB_EC.dat.10.backup --start 2021-01-01 --end 2021-12-31 --output /Users/xx/data/master_met/input/Flux.csv ```
<<<<<<< HEAD
- There is a GUI application for this. Run metmerger.py under ameriflux_pipeline directory
  by typing `python metmerger.py` in command prompt after cd into ameriflux_pipleline directory.
  
6. Set necessary parameters for pre and post processing of PyFluxPro and EddyPro
=======
- This creates a csv file with merged data from the raw dat files and a log file met_merger.log.

8. Set necessary parameters for pre and post processing of PyFluxPro and EddyPro
>>>>>>> 57cd9552cca8a5e0135886bf0a26276f7e593a55
- This can be done by creating .env file under ameriflux_pipeline directory, or directly change the values in config.py
- Give the full path to all input and output file location.
- There is a GUI application for this. Run enveditor.py under ameriflux_pipeline directory 
  by typing `python enveditor.py` in command prompt after cd into ameriflux_pipleline directory (recommended).
- Details about the parameters are describes in the section 9 below

7. To run python module for processing till PyFluxPro L1 and L2 control files, please run:
```
python pre_pyfluxpro.py
```
This creates 
- master met data, 
- master met data formatted for eddypro, 
- eddypro full output, 
- pyfluxpro input excel sheet, 
- pyfluxpro input excel sheet formatted for Ameriflux, 
- L1 and L2 control files formatted for Ameriflux,
- log file pre_pyfluxpro.log, and log file for eddypro run in eddypro output folder.

8. Run PyFluxPro version 3.3.2 with the generated L1 and L2 control files to produce graphs and perform quality checks on the data.

9. To run python module for post processing of PyFluxPro L2 run output to produce Ameriflux-ready data, please run:
```
python post_pyfluxpro.py
```
This produces a csv file that is Ameriflux-friendly in the same directory as the L2 run output. The log file is post_pyfluxpro.log.

10. Example .env file
- Using enveditor.py is recommended than directly modifying config.py file or .env file.
- There are buttons for more information and description on each item.
- Save button at the bottom will generate .env file in the proper location.
- There are several groups of variables in the editor
- Sync files from the server 
  - allows the user to sync the ghg files and met files 
  - need to provide server url and auth information, such as username and password
  - need to set up the file path from the server and local machine
  - only runs when the confirmation is set to 'Y'
- Variables for EddyPro formatting
  - files or variables needed for formatting the eddypro input file
- Variables for EddyPro running
  - files or parameters needed for running the eddypro headless
- Variables for PyFluxPro running
  - output from eddypro run is needed
  - input and output files that are needed for pyfluxpro running
- Variables for PyFluxPro AmeriFlux formatting
  - parameters for input and outputs for making pyfluxpro inputs with AmeriFlux formatting
  
```
# Sync files from the server
SFTP_CONFIRMATION=N
SFTP_SERVER=remote.serverl.url
SFTP_USERNAME=username
SFTP_PASSWORD=password
SFTP_GHG_REMOTE_PATH=/path/in/the/remote/server/
SFTP_GHG_LOCAL_PATH=/path/in/the/local/machine/
SFTP_MET_REMOTE_PATH=/path/in/the/remote/server/
SFTP_MET_LOCAL_PATH=/path/in/the/local/machine/

# Variables for EddyPro formatting
MISSING_TIME_USER_CONFIRMATION=Y
INPUT_MET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/FLUXSB_EC_JanMar2021.csv
INPUT_PRECIP=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/Precip_IWS_Jan-Feb_2021.xlsx
MISSING_TIME=96
MASTER_MET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/output/met_output.csv
INPUT_SOIL_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/input/Soils_key.xlsx

# Variables for EddyPro running
EDDYPRO_BIN_LOC=/Applications/eddypro.app/Contents/MacOS/bin
EDDYPRO_PROJ_FILE_NAME=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/input/EddyPro_Run_Template.eddypro
EDDYPRO_PROJ_TITLE=AmeriFlux_Pipeline
EDDYPRO_PROJ_ID=ameriflux_pipeline
EDDYPRO_FILE_PROTOTYPE=yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
EDDYPRO_PROJ_FILE=/Users/xxx/2021-01-01T000000_Sorghum-00137.metadata
EDDYPRO_DYN_METADATA=/Users/xxx/Sorghum_2021_dynamic_metadata.csv
EDDYPRO_OUTPUT_PATH=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/output/
EDDYPRO_INPUT_GHG_PATH=/Users/xxx/Raw_Jan-Mar_2021_GHG_Files/

# Variables for PyFluxPro running
FULL_OUTPUT_PYFLUXPRO=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/full_output.csv
MET_DATA_30_PYFLUXPRO=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/Met_data_30.csv
PYFLUXPRO_INPUT_SHEET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/pyfluxpro_input.xlsx
PYFLUXPRO_INPUT_AMERIFLUX=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/pyfluxpro_input_ameriflux.xlsx

# Variables for PyFluxPro AmeriFlux formatting
AMERIFLUX_VARIABLE_USER_CONFIRMATION=N
L1_MAINSTEM_INPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/L1.txt
L1_AMERIFLUX_ONLY_INPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L1_ameriflux_only.txt
L1_AMERIFLUX_MAINSTEM_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/Ameriflux-Mainstem-Key.xlsx
L1_AMERIFLUX_RUN_OUTPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/Sorghum_2021_L1.nc
L1_AMERIFLUX=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L1_ameriflux.txt
L1_AMERIFLUX_ERRORING_VARIABLES_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/L1_erroring_variables.xlsx

L2_MAINSTEM_INPUT=/Users/xxx/data/pyfluxpro/input/L2_mainstem.txt
L2_AMERIFLUX_ONLY_INPUT=/Users/xxx/data/pyfluxpro/input/L2_AF.txt
L2_AMERIFLUX_RUN_OUTPUT=/Users/xxx/data/pyfluxpro/generated/Sorghum_2021_L2.nc
L2_AMERIFLUX=/Users/xxx/data/pyfluxpro/generated/L2_ameriflux.txt
```
