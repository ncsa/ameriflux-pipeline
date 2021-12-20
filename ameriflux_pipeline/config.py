# configs file
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """
    class to list all configuration settings required for preprocessing and formatting for EddyPro and PyFluxPro
    """
    # input data for creating master meteorology data
    # parent data folder to store all input and output data files
    DATA_ROOT = os.getenv('DATA_ROOT', '/Users/ameriflux-pipeline/ameriflux_pipeline/data/')
    # input met data path. relative to parent data folder
    INPUT_MET = os.getenv('INPUT_MET', os.path.join(DATA_ROOT, 'master_met', 'input', 'FLUXSB_EC_JanMar2021.csv'))
    # input precipitation data. Path relative to parent data folder
    INPUT_PRECIP = os.getenv('INPUT_PRECIP',
                             os.path.join(DATA_ROOT, 'master_met', 'input', 'Precip_IWS_Jan-Feb_2021.xlsx'))
    # Number of missing timeslot threshold for user confirmation to insert
    MISSING_TIME = os.getenv('MISSING_TIME', 96)
    # NOTE 9
    # User confirmation to insert large number of missing timestamps
    # Enter 'Y'/'YES' to insert, 'N'/'NO' to ignore and 'A'/'ASK' to await user input during runtime.
    USER_CONFIRMATION = os.getenv('USER_CONFIRMATION', 'Y')
    # master met output data path. Path relative to parent data folder
    MASTER_MET = os.getenv('MASTER_MET', os.path.join(DATA_ROOT, 'master_met', 'output', 'met_output.csv'))

    # input data for formatting Eddypro master meteorology data.
    # input soil key data path. Path relative to parent data folder
    INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY', os.path.join(DATA_ROOT, 'eddypro', 'input', 'Soils_key.xlsx'))

    # eddypro related parameters
    # bin folder location of eddypro_rp exec file
    EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC', '')  # '/Applications/eddypro.app/Contents/MacOS/bin'
    # EddyPro run template. Path relative to parent data folder
    EDDYPRO_PROJ_FILE_NAME = os.getenv('EDDYPRO_PROJ_FILE_NAME',
                                       os.path.join(DATA_ROOT, 'eddypro', 'input', 'EddyPro_Run_Template.eddypro'))
    EDDYPRO_PROJ_TITLE = os.getenv('EDDYPRO_PROJ_TITLE', 'AmeriFlux_Pipeline')
    EDDYPRO_PROJ_ID = os.getenv('EDDYPRO_PROJ_ID', 'ameriflux_pipeline')
    EDDYPRO_FILE_PROTOTYPE = os.getenv('EDDYPRO_FILE_PROTOTYPE', 'yyyy-mm-ddTHHMM??_Sorghum-00137.ghg')
    # EddyPro input metadata file from GHG. Path relative to parent data folder
    EDDYPRO_PROJ_FILE = os.getenv('EDDYPRO_PROJ_FILE', os.path.join(DATA_ROOT, 'eddypro', 'input',
                                                                    '2021-01-01T000000_Sorghum-00137.metadata'))
    # EddyPro input dynamic metadata file. Path relative to parent data folder
    EDDYPRO_DYN_METADATA = os.getenv('EDDYPRO_DYN_METADATA',
                                     os.path.join(DATA_ROOT, 'eddypro', 'input', 'Sorghum_2021_dynamic_metadata.csv'))
    # EddyPro input GHG files folder. Path relative to parent data folder
    EDDYPRO_INPUT_GHG_PATH = os.getenv('EDDYPRO_INPUT_GHG_PATH',
                                       os.path.join(DATA_ROOT, 'eddypro', 'input', 'Raw Jan-Mar 2021 GHG Files'))
    # EddyPro output folder. Path relative to parent data folder
    EDDYPRO_OUTPUT_PATH = os.getenv('EDDYPRO_OUTPUT_PATH', os.path.join(DATA_ROOT, 'eddypro', 'output'))

    # PyFluxPro related data
    FULL_OUTPUT_PYFLUXPRO = os.getenv('FULL_OUTPUT_PYFLUXPRO',
                                      os.path.join(DATA_ROOT, 'pyfluxpro', 'input', 'full_output.csv'))
    MET_DATA_30_PYFLUXPRO = os.getenv('MET_DATA_30_PYFLUXPRO',
                                      os.path.join(DATA_ROOT, 'pyfluxpro', 'input', 'Met_data_30.csv'))
    PYFLUXPRO_INPUT_SHEET = os.getenv('PYFLUXPRO_INPUT_SHEET',
                                      os.path.join(DATA_ROOT, 'pyfluxpro', 'input', 'pyfluxpro_input.xlsx'))

    # QA/QC values
    # precipitation threshold values used in creating Eddypro master meteorology data
    QC_PRECIP_LOWER = 0.0  # precipitation lower threshold value (inches)
    QC_PRECIP_UPPER = 0.2  # precipitation upper threshold value (inches)
