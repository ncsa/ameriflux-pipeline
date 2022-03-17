# AmeriFlux-pipeline

**AmeriFlux-pipeline** is an automated process of handling flux data for AmeriFlux submission.
This automated code creates master met data, runs EddyPro automatically and creates input sheet for PyfluxPro input.

## Prerequisites

### Requirements
- Python 3.8+
- EddyPro 7.0.6 (https://www.licor.com/env/support/EddyPro/software.html) exec files
- PyFluxPro 3.2.0+ (https://github.com/OzFlux/PyFluxPro)

## Files :
- master_met/preprocessor.py creates the master met data file
- eddypro/eddyproformat.py creates master met data formatted for eddypro headless run
- eddypro/runeddypro.py is responsible for the eddypro headless run
- pyfluxpro/pyfluxproformat.py creates the input excel sheet for pyfluxpro
- utils/data_util.py performs data write operations
- enveditor.py is the GUI for helping the users to set the input and output data
- main.py is the main file to run.
- config.py lists all configurations
- requirements.txt lists the required packages

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
virtualenv -p python3 venv
source venv/bin/activate
```
- (Windows):
```
python -m venv env
.\env\Scripts\activate
```

4. Install dependencies:
- The model is tested on Python 3.8, with dependencies listed in requirements.txt.
- To install these Python dependencies, please run following command in your virtual env
```
pip install -r requirements.txt
```
- Or if you prefer to use conda,
```
conda install --file requirements.txt
```

5. Set necessary parameters
- This can be done by creating .env file under ameriflux_pipeline directory, or directly change the values in config.py
- Give the full path to all input and output file location.
- There is a GUI application for this. Run enveditor.py under ameriflux_pipeline directory 
  by typing `python enveditor.py` in command prompt after cd into ameriflux_pipleline directory.
- Details about the parameters are describes in the section 7 below

6. To run python module with default parameters, please run:
```
python main.py
```

7. Example .env file
- Using enveditor.py is recommended than directly modifying config.py file or .env file.
- There are buttons for more information and description in each items.
- Save will generate .env file in the proper location.
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
MISSING_TIME_USER_CONFIRMATION=A
INPUT_MET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/FLUXSB_EC_JanMar2021.csv
INPUT_PRECIP=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/Precip_IWS_Jan-Feb_2021.xlsx
MISSING_TIME=96
USER_CONFIRMATION='Y'
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
AMERIFLUX_VARIABLE_USER_CONFIRMATION=Y
L1_MAINSTEM_INPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/L1.txt
L1_AMERIFLUX_ONLY_INPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L1_ameriflux_only.txt
L1_AMERIFLUX_MAINSTEM_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/Ameriflux-Mainstem-Key.xlsx
L1_AMERIFLUX_RUN_OUTPUT=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/Sorghum_2021_L1.nc
L1_AMERIFLUX=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L1_ameriflux.txt
L1_AMERIFLUX_ERRORING_VARIABLES_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/L1_erroring_variables.xlsx

```
