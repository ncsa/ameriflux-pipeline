# AmeriFlux-pipeline

**AmeriFlux-pipeline** is an automated process of handling flux data <br>
TODO: need to revised and rewritten

## Prerequisites

* Requirements: Python 3.8+, Anaconda or Miniconda.
## Files :
- data
  - csv files to be processed for EddyPro
- preprocessing.py takes care of the data preprocessing steps
- main.py is the main file to run.
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
3. Install dependencies: The model is tested on Python 3.8, with dependencies listed in requirements.txt. To install these Python dependencies, please run
```
pip install -r requirements.txt
```
Or if you prefer to use conda,
```
conda install --file requirements.txt
```

## Usage :
1. Set necessary parameters.
   This can be done by creating .env file under ameriflux_pipeline directory, or directry change the values in config.py

example .env file
```
# input data for formating EddyPro master meteology data
INPUT_MET=tests/data/FLUXSB_EC_JanMar2021.csv  # input met data path
INPUT_PRECIP=tests/data/Precip_IWS_Jan-Feb_2021.xlsx  # input precipitation data path
MISSING_TIME=96  # Number of 30min missing timeslot threshold for user confirmation
INPUT_SOIL_KEY=tests/data/Soils key.xlsx  # input soil key data path
MASTER_MET=tests/data/met_output.csv  # output data path for master met data
EDDYPRO_FULL_OUTPUT=tests/data/eddypro_full_output.csv  # full outputs from eddypro

# input data for running EddyPro
EDDYPRO_BIN_LOC=C:/Program Files/LI-COR/EddyPro-7.0.7/bin  # directory path to eddypro bin folder
EDDYPRO_PROJ_FILE_NAME=ameriflux_pipeline/templates/EddyPro_Run_Template.eddypro
EDDYPRO_PROJ_TITLE=AmeriFlux_Pipeline
EDDYPRO_PROJ_ID=ameriflux_pipeline
EDDYPRO_FILE_PROTOTYPE=yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
EDDYPRO_PROJ_FILE=C:/Users/xxx/Documents/Ameriflux/Data/sample_test/2021-01-01T000000_Sorghum-00137.metadata
EDDYPRO_DYN_METADATA=C:/Users/xxx/Documents/Ameriflux/Data/sample_test/Sorghum_2021_dynamic_metadata.csv
EDDYPRO_OUTPUT_PATH=C:/Users/xxx/Documents/Ameriflux/Data/sample_test/test_output
EDDYPRO_INPUT_GHG_PATH=C:/Users/xxx/Documents/Ameriflux/Data/sample_test/sample_ghg_files

# PyFluxPro related data
FULL_OUTPUT_PYFLUXPRO = 'tests/data/full_output.csv'
MET_DATA_30_PYFLUXPRO = 'tests/data/Met_data_30.csv'
```
2. To run python module with default parameters, please run:
```
python main.py
```
