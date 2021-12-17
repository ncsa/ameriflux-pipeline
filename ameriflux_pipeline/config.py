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
    INPUT_MET = os.getenv('INPUT_MET', 'data/master_met/input/FLUXSB_EC_JanMar2021.csv')  # input met data path
    INPUT_PRECIP = os.getenv('INPUT_PRECIP', 'data/master_met/input/Precip_IWS_Jan-Feb_2021.xlsx')  # input precipitation data path
    MISSING_TIME = os.getenv('MISSING_TIME', 96)  # Number of missing timeslot threshold for user confirmation to insert
    # NOTE 9
    # User confirmation to insert large number of missing timestamps
    # Enter 'Y'/'YES' to insert, 'N'/'NO' to ignore and 'A'/'ASK' to await user input during runtime.
    USER_CONFIRMATION = os.getenv('USER_CONFIRMATION', 'Y')
    MASTER_MET = os.getenv('MASTER_MET', 'tests/data/met_output.csv')  # output data path

    # input data for formatting Eddypro master meteorology data
    INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY', 'data/eddypro/input/Soils_key.xlsx')  # input soil key data path

    # eddypro related parameters
    # bin folder location of eddypro_rp exec file
    EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC', '')  # '/Applications/eddypro.app/Contents/MacOS/bin'
    EDDYPRO_PROJ_FILE_NAME = os.getenv('EDDYPRO_PROJ_FILE_NAME', 'templates/EddyPro_Run_Template.eddypro')
    EDDYPRO_PROJ_TITLE = os.getenv('EDDYPRO_PROJ_TITLE', 'AmeriFlux_Pipeline')
    EDDYPRO_PROJ_ID = os.getenv('EDDYPRO_PROJ_ID', 'ameriflux_pipeline')
    EDDYPRO_FILE_PROTOTYPE = os.getenv('EDDYPRO_FILE_PROTOTYPE', 'yyyy-mm-ddTHHMM??_Sorghum-00137.ghg')
    EDDYPRO_PROJ_FILE = os.getenv('EDDYPRO_PROJ_FILE', 'data/eddypro/input/2021-01-01T000000_Sorghum-00137.metadata')
    EDDYPRO_DYN_METADATA = os.getenv('EDDYPRO_DYN_METADATA', 'data/eddypro/input/Sorghum_2021_dynamic_metadata.csv')
    EDDYPRO_INPUT_GHG_PATH = os.getenv('EDDYPRO_INPUT_GHG_PATH', 'data/eddypro/input/Raw Jan-Mar 2021 GHG Files')
    EDDYPRO_OUTPUT_PATH = os.getenv('EDDYPRO_OUTPUT_PATH', 'data/eddypro/output/test_output')


    # PyFluxPro related data
    FULL_OUTPUT_PYFLUXPRO = os.getenv('FULL_OUTPUT_PYFLUXPRO', 'data/pyfluxpro/input/full_output.csv')
    MET_DATA_30_PYFLUXPRO = os.getenv('MET_DATA_30_PYFLUXPRO', 'data/pyfluxpro/input/Met_data_30.csv')
    PYFLUXPRO_INPUT_SHEET = os.getenv('PYFLUXPRO_INPUT_SHEET', 'data/pyfluxpro/input/pyfluxpro_input.xlsx')

    # QA/QC values
    # precipitation threshold values used in creating Eddypro master meteorology data
    QC_PRECIP_LOWER = 0.0  # precipitation lower threshold value (inches)
    QC_PRECIP_UPPER = 0.2  # precipitation upper threshold value (inches)
