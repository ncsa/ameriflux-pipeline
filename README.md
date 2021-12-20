# AmeriFlux-pipeline

**AmeriFlux-pipeline** is an automated process of handling flux data for AmeriFlux submission.
This automated code creates master met data, runs EddyPro automatically and creates input sheet for PyfluxPro input.

## Prerequisites

###Requirements
- Python 3.8+
- EddyPro 7 (https://www.licor.com/env/support/EddyPro/software.html) exec files

## Files :
- data/
  - Input and output data files are located here by default.
  - The user also has the option to provide full data path to all input and output files in config or .env file
  - eddypro/input contains the input files for running eddypro
  - eddypro/output contains the output files from eddypro headless run
  - master_met/input contains the input files for creating master met data
  - master_met/output is the location where the code writes the master met data
  - pyfluxpro/input contains the input file for pyfluxpro. This is generated by the program.
  - pyfluxpro/output contains the output files from pyfluxpro headless run.
- master_met/preprocessor.py creates the master met data file
- eddypro/eddyproformat.py creates master met data formatted for eddypro headless run
- eddypro/runeddypro.py is responsible for the eddypro headless run
- pyfluxpro/pyfluxproformat.py creates the input excel sheet for pyfluxpro
- utils/data_util.py performs data write operations
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
3. Set necessary parameters
- This can be done by creating .env file under ameriflux_pipeline directory, or directly change the values in config.py
- Please give the full path to all input and output file location.
- Example .env file
```
INPUT_MET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/FLUXSB_EC_JanMar2021.csv
INPUT_PRECIP=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/input/Precip_IWS_Jan-Feb_2021.xlsx
MISSING_TIME=96
USER_CONFIRMATION='Y'
MASTER_MET=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/master_met/output/met_output.csv

INPUT_SOIL_KEY=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/input/Soils_key.xlsx

EDDYPRO_BIN_LOC=/Applications/eddypro.app/Contents/MacOS/bin
EDDYPRO_PROJ_FILE_NAME=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/input/EddyPro_Run_Template.eddypro
EDDYPRO_PROJ_TITLE=AmeriFlux_Pipeline
EDDYPRO_PROJ_ID=ameriflux_pipeline
EDDYPRO_FILE_PROTOTYPE=yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
EDDYPRO_PROJ_FILE=/Users/xxx/2021-01-01T000000_Sorghum-00137.metadata
EDDYPRO_DYN_METADATA=/Users/xxx/Sorghum_2021_dynamic_metadata.csv
EDDYPRO_OUTPUT_PATH=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/output/
EDDYPRO_INPUT_GHG_PATH=/Users/xxx/Raw_Jan-Mar_2021_GHG_Files/

FULL_OUTPUT_PYFLUXPRO=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/full_output.csv
MET_DATA_30_PYFLUXPRO=/Users/xxx/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/Met_data_30.csv

QC_PRECIP_LOWER=0.0
QC_PRECIP_UPPER=0.2
```
4. Setup virtual environment :
```
python3 -m venv venv
source venv/bin/activate
```

5. Install dependencies: 
- The model is tested on Python 3.8, with dependencies listed in requirements.txt. 
- To install these Python dependencies, please run
```
pip install -r requirements.txt
```
Or if you prefer to use conda,
```
conda install --file requirements.txt
```

6. To run python module with default parameters, please run:
```
python main.py
```
