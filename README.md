# Crop2Ameriflux

## Overview
**Crop2Ameriflux** is an automated data pipeline that converts raw data files to Ameriflux FP format with minimal user interaction. 

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

1. Get the GitHub repository
- Get a copy of the repository by either
  - git clone command using Git ```git clone https://github.com/ncsa/ameriflux-pipeline.git``` or
  - downloading the repository from [github](https://github.com/ncsa/ameriflux-pipeline) "Download ZIP" button.

2. Change working directory
- In terminal, cd to repository by ```cd ameriflux-pipeline```

3. Set up python virtual environment
  - Using conda (recommended)
  ```
  conda create --prefix=venv python=3.8
  conda activate venv
  ```
  - Using Python virtualenv package
    - Linux or MAC:
    ```
    virtualenv -p python3.8 venv
    source venv/bin/activate
    ```
    - Windows:
    ```
    python -m venv env
    .\env\Scripts\activate
    ```

4. Install dependencies:
- The pipeline is tested on Python 3.8, with dependencies listed in requirements.txt.
- To install these Python dependencies, please run following command in your virtual environment
```
pip install -r requirements.txt
```

5. To run python modules, cd to ameriflux_pipeline directory ```cd ameriflux_pipeline```

6. If multiple dat files needs to be merged for a specific time span of meteorological data, user can execute the [metprocessor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/metprocessor.md) module by either GUI or command line.
- run ```python metprocessor.py``` to launch a GUI 
- run ```python met_data_processor.py``` in command line
  - To request all command line parameters, please run ```python met_data_processor.py --help``` 
  - data parameter takes in comma separated file paths. This is a mandatory field. If not specified, the code will ask for user inputs at run time.
  - start parameter takes in the start date for merger, given in yyyy-mm-dd format. This will later be expanded to support any plausible date formats. If not given, by default it takes in 2021-01-01
  - end parameter takes in the end date for merger, given in yyyy-mm-dd format. This will later be expanded to support any plausible date formats. If not given, by default it takes in 2021-12-31
  - output parameter takes in the full output path of a csv file which will write the merged output to. By default it will write to master_met/input/Flux.csv
  - key parameter takes in an excel file that lets user rename met tower variables. If not specified, variables are not renamed. This is the default behaviour.
  - To run the python module with default parameters run ```python met_data_processor.py```
  - Run command example with all arguments:  
  ``` python met_data_processor.py --data /Users/xx/data/master_met/input/FluxSB_EC.dat,/Users/xx/data/master_met/input/FluxSB_EC.dat.9.backup,/Users/xx/data/master_met/input/FluxSB_EC.dat.10.backup --start 2021-01-01 --end 2021-12-31 --key /Users/xx/master_met/input/metmerger_key.xlsx --output /Users/xx/data/master_met/input/Flux.csv ```
- This creates a csv file with merged data from the raw dat files and a log file met_processor.log.

6. Set necessary parameters for the pipeline execution
- Users can configure the settings for the pipeline by using the [GUI](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md)(recommended) or directly modifying the .env file
- Execute `python enveditor.py` in command prompt to launch the GUI.
- Or if you prefer to modify the .env file
  - Give the full path to all input and output file location.
- Details about the parameters are describes in the section 10 below

7. To execute the pipeline as per user configurations, users can choose to run via GUI (recommended) by using command line.
   1. Execute the [pre-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/prepyfluxpro.md) module, which does all processing till the generation of Pyfluxpro L1 and L2 control files
      - run ```python pipeline.py``` to launch a GUI and click the "Run" button for "Run Pre-Pyfluxpro process" OR 
      - run ```python pre_pyfluxpro.py``` in command line
      - This creates 
        - master meteorological data, 
        - master meteorological data formatted for eddypro, 
        - eddypro full output, 
        - pyfluxpro input excel sheet, 
        - pyfluxpro input excel sheet formatted for Ameriflux, 
        - L1 and L2 control files formatted for Ameriflux,
        - log file pre_pyfluxpro.log, and log file for eddypro run in eddypro output folder.
   2. Launch the PyFluxPro software by following the instructions [here](https://github.com/OzFlux/PyFluxPro).
      - Run PyFluxPro version 3.3.2 with the generated L1 and L2 control files to produce graphs and perform quality checks on the data.
      - Make changes to the [settings](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) or data if neccessary and re-run the pre-pyfluxpro module
   3. Execute the [post-pyfluxpro](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/postpyfluxpro.md) module to create the Ameriflux submission-ready csv file.
      - run ```python pipeline.py``` to launch a GUI and click the "Run" button for "Run Post-Pyfluxpro process" OR 
      - run ```python post_pyfluxpro.py``` in command line
      - The log file is post_pyfluxpro.log.
   4. Users can choose to execute sub-modules within the pre-pyfluxpro module. See [pipeline](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/pipeline.md) module for details

8. Example .env file
- User settings for the entire pipeline run is read from the .env file
- Using [enveditor](https://github.com/ncsa/ameriflux-pipeline/blob/develop/docs/enveditor.md) GUI is recommended to change the configurations, rather than directly modifying config.py file or .env file.
- There are buttons for more information and description on each item. 
- All settings has a default set value (including input file paths and file types).
- Save button at the bottom will generate .env file in the proper location.
- See .example.env for a template .env file
  

## Repository Files :
- ameriflux-pipeline is the main github repo
- CONTRIBUTORS : lists the contributors of the repo
- CHANGELOG lists all changes made to the code with links to the issues.
- NOTES : all decisions made is tagged and represented in code.
- README : user guide for installing and running the program.
- requirements.txt : list of required packages
- docs / directory contains detailed documentation on all modules
- tests / directory contains the unit tests
- ameriflux_pipeline/ : runnable python modules (dir)
  - enveditor.py is the GUI for helping the users to set the input and output data
  - config.py lists all configurations
  - requirements.txt lists the required packages
  - metprocessor.py is the GUI for helping the users to merge multiple meteorology data to single one with given start and end date
  - met_data_processor.py merges multiple .dat files containing raw met data to a csv file that can then be used in the pipeline.
  - pre_pyfluxpro.py runs all processing steps till PyFluxPro runs. It generates L1 and L2 control files as per Ameriflux standards
  - post_pyfluxpro.py runs all post processing steps to convert the L2 run output to csv file required for Ameriflux submission.
  - pipeline.py launches a GUI for modularized run of the modules.
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
  - data/ folder stores all data. Output dir stores outputs generated by code. Input dir stores the inputs required for the module run.
    - README file present for each location describes the typical files in that directory
    - master_met/ input : stores all data required for creating master meteorological data
    - master_met/ output : data outputs from mastermetprocessor
    - eddypro/ input : all data required for eddypro module
    - eddypro/ templates : eddypro project template file to run EddyPro software
    - eddypro/ output : data outputs from eddypro module
    - pyfluxpro/ input : data inputs for pyfluxpro processor module
    - pyfluxpro/ output : data outputs from pyfluxpro processor module
    - Users are free to choose any data storage location. This is just a recommended approach.
