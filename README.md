# Crop2Ameriflux

## Overview
**Crop2Ameriflux** is an automated data pipeline that converts raw data files to Ameriflux [FP format](https://ameriflux.lbl.gov/data/uploading-half-hourly-hourly-data/) with minimal user interaction. 

**Ameriflux-Pipeline** is a suite of python modules designed for this purpose. We integrate EddyPro and PyFluxPro software using high-quality open-source tools and libraries, reducing processing time and human error to enable more frequent contributions to Ameriflux. The raw data undergo a series of transformations including time format conventions, variable processing and handling of missing data. The final output of this streamlined process is a csv file that is publishable to Ameriflux. By integrating EddyPro and PyFluxPro along with automating all data transformation and quality checks, Crop2Ameriflux increases the reliability and accuracy of data while reducing the processing time.
This automated code creates master meteorological data, runs EddyPro automatically and creates inputs for PyfluxPro software.

### Features
- Automation of data processing for Eddypro and Pyfluxpro.
- Seamless run of EddyPro software within the pipeline.
- Highly modularized, robust and documented code
- Validations done before and after each process
- Gives users the ability to configure the settings
- GUI and command line interfaces
- All processes are logged
- Immense reduction in processing time

## Prerequisites

### Requirements
- Python 3.8
- EddyPro 7.0.6 (https://www.licor.com/env/support/EddyPro/software.html) exec files
- PyFluxPro 3.3.2 (https://github.com/OzFlux/PyFluxPro)

## Installation

1. Get the code from GitHub repository
- Get a copy of the repository to your local machine.
  - Using Git clone ```git clone https://github.com/ncsa/ameriflux-pipeline.git``` 
  - OR if you prefer to download a zip file, click "Download ZIP button" in [repo](https://github.com/ncsa/ameriflux-pipeline).

2. Change working directory
- In terminal, cd to repository by typing ```cd ameriflux-pipeline```

3. Set up python virtual environment
  - Using conda (recommended)
  ```
  conda create --prefix=venv python=3.8
  conda activate venv
  ```
  - OR if you prefer python virtualenv package
    - Linux or MAC:
    ```
    virtualenv -p python3.8 venv
    source venv/bin/activate
    ```
    - Windows:
    ```
    python3 -m venv env
    .\env\Scripts\activate
    ```

4. Install dependencies:
- The pipeline is tested on Python 3.8, with dependencies listed in [requirements.txt](https://github.com/ncsa/ameriflux-pipeline/blob/develop/requirements.txt).
- To install these Python dependencies, please run following command terminal within the newly created virtual environment
```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. To run python modules, cd to ameriflux_pipeline directory ```cd ameriflux_pipeline```

6. If multiple dat files needs to be merged for a specific time span of meteorological data, user can execute the [metprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/metprocessor.md) module by either GUI or command line.
- Using GUI (recommended)
  - type ```python metprocessor.py``` in command prompt/terminal. 
- OR to use the command line option
  - type ```python met_data_processor.py``` in command prompt/terminal
    - To request all command line parameters, please run ```python met_data_processor.py --help``` 
    - To run the python module with default parameters run ```python met_data_processor.py```
    - Run command example with all arguments:  
    ``` python met_data_processor.py --data /Users/xx/data/master_met/input/FluxSB_EC.dat,/Users/xx/data/master_met/input/FluxSB_EC.dat.9.backup,/Users/xx/data/master_met/input/FluxSB_EC.dat.10.backup --start 2021-01-01 --end 2021-12-31 --key /Users/xx/master_met/input/metmerger_key.xlsx --output /Users/xx/data/master_met/input/Flux.csv ```
    - For more information on the parameters, check the [metprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/metprocessor.md) documentation
- This creates a csv file with merged data from the raw dat files and a log file met_processor.log.

7. Set necessary parameters for the pipeline execution
- Users can configure the settings for the pipeline by using the [enveditor GUI](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) (recommended) or directly modifying the .env file
  - Using GUI
    - Type `python enveditor.py` in command prompt/terminal to launch the GUI.
    - There are buttons for more information and description on each item. 
    - All settings have a default value (including input file paths and file types).
    - Save button at the bottom will generate .env file in the proper location.
  - OR if you prefer to modify the .env file
    - Give the full path to all input and output file locations.
    - See [.example-env](https://github.com/ncsa/ameriflux-pipeline/blob/develop/ameriflux_pipeline/.example-env) for a template .env file
- These settings will be used to run the pipeline as described in step 8.
- Details about the parameters are described in [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md).

8. Once the configurations are set, users can run by pipeline via GUI (recommended) or command line. The [pipeline](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pipeline.md) is modularized to enable users to run each module separately.
   1. Execute the [pre-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) module, which does all processing till the generation of Pyfluxpro L1 and L2 control files
      - Using GUI (recommended)
        - Type ```python pipeline.py``` in command prompt/terminal to launch a GUI and click the "Run" button for "Run Pre-Pyfluxpro process".
      - OR to use the command line option
        - Type ```python pre_pyfluxpro.py``` in command prompt/terminal.
      - The pre-pyfluxpro module creates 
        - master meteorological data, 
        - master meteorological data formatted for eddypro, 
        - eddypro full output, 
        - pyfluxpro input excel sheet, 
        - pyfluxpro input excel sheet formatted for Ameriflux, 
        - L1 and L2 control files formatted for Ameriflux,
        - log file pre_pyfluxpro.log, and log file for eddypro run in eddypro output folder.
   2. Launch the PyFluxPro software by following the instructions [here](https://github.com/OzFlux/PyFluxPro).
      - Run PyFluxPro version 3.3.2 with the generated L1 and L2 control files to produce graphs and perform quality checks on the data.
      - Make changes to the [settings](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) or data and re-run the pre-pyfluxpro module (or sub-modules) if necessary.
   3. Execute the [post-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/postpyfluxpro.md) module to create the Ameriflux submission-ready csv file.
      - Using GUI (recommended)
        - Type ```python pipeline.py``` in command prompt/terminal to launch a GUI and click the "Run" button for "Run Post-Pyfluxpro process".
      - OR to use the command line option
        - Type ```python post_pyfluxpro.py``` in command prompt/terminal. 
      - The post-pyfluxpro module creates 
        - Ameriflux submission-ready csv file,
        - log file post_pyfluxpro.log
   4. Users can choose to execute sub-modules within the pre-pyfluxpro module. See [pipeline](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pipeline.md) module for details. 

## Repository Files :
- ameriflux-pipeline : the main GitHub repo.
- CONTRIBUTORS : lists the contributors of the repo.
- CHANGELOG : lists all changes made to the code with links to the issues.
- NOTES : all decisions made is tagged and represented in code.
- README : user guide for installing and running the program.
- requirements.txt : list of required packages.
- docs / directory : contains detailed documentation on all modules.
- tests / directory : contains the unit tests.
- ameriflux_pipeline/ : runnable python modules (dir).
  - enveditor.py : GUI for setting the configurations for the pipeline.
  - config.py : lists all configurations.
  - metprocessor.py : GUI to merge multiple raw meteorology data to a single csv file with given start and end date.
  - met_data_processor.py : merges multiple .dat files containing raw met data to a csv file that can then be used in the pipeline.
  - pre_pyfluxpro.py : runs all processing steps till PyFluxPro software. It generates L1 and L2 control files as per Ameriflux standards and other required data files for PyFluxPro software run.
  - post_pyfluxpro.py : runs all post processing steps to convert the L2 run output to csv file required for Ameriflux submission.
  - pipeline.py : launches a GUI for modularized run of the pipeline.
  - master_met / mastermetprocessor.py : creates the master meteorological data file.
  - eddypro / eddyproformat.py : creates master meteorological data formatted for EddyPro.
  - eddypro / runeddypro.py : is responsible for the EddyPro headless run within the pipeline.
  - pyfluxpro / pyfluxproformat.py : creates the input excel sheet for PyFluxPro.
  - pyfluxpro / amerifluxformat.py : creates the input excel sheet for PyFluxPro as per Ameriflux standards.
  - pyfluxpro / l1format.py : creates L1 control file as per Ameriflux standards.
  - pyfluxpro / l2format.py : creates L2 control file as per Ameriflux standards.
  - pyfluxpro / outputformat.py : creates csv file with data formatted for Ameriflux submission from the L2 run output.
  - utils / syncdata.py : performs syncing of GHG data with remote server location.
  - utils / data_util.py : performs various data operations.
  - utils / input_validation.py : performs validations on user inputs from the env file.
  - utils / process_validation.py : performs validations on data.
  - data/ : folder stores all data. Output directory stores outputs generated by code. Input directory stores the inputs required for the module.
    - README : file describes the typical files in that directory.
    - master_met/ input : stores all data required for creating master meteorological data.
    - master_met/ output : data outputs from mastermetprocessor module.
    - eddypro/ input : all data required for eddypro module.
    - eddypro/ templates : eddypro project template file to run EddyPro software.
    - eddypro/ output : data outputs from eddypro module.
    - pyfluxpro/ input : data inputs for pyfluxpro module.
    - pyfluxpro/ output : data outputs from pyfluxpro module.
    - Users are free to choose any data storage location. This is just a recommended approach.
