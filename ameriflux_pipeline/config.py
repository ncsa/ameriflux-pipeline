# configs file
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """
    class to list all configuration settings required for preprocessing and formatting
    """
    # input data for Eddypro master meteorology data
    INPUT_MET = os.getenv('INPUT_MET', 'tests/data/FLUXSB_EC_JanMar2021.csv')  # input met data path
    INPUT_PRECIP = os.getenv('INPUT_PRECIP', 'tests/data/Precip_IWS_Jan-Feb_2021.xlsx')  # input precipitation data path
    MISSING_TIME = os.getenv('MISSING_TIME', 96)  # Number of 30min missing timeslot threshold for user confirmation
    INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY', 'tests/data/Soils key.xlsx')  # input soil key data path
    MASTER_MET = os.getenv('MASTER_MET', 'tests/data/met_output.csv')  # output data path

    # eddypro related parameters
    # folder location of eddypro_rp exec file
    EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC', '')
    EDDYPRO_PROJ_FILE_NAME = os.getenv('EDDYPRO_PROJ_FILE_NAME', 'templates/EddyPro_Run_Template.eddypro')
    EDDYPRO_PROJ_TITLE = os.getenv('EDDYPRO_PROJ_TITLE', 'AmeriFlux_Pipeline')
    EDDYPRO_PROJ_ID = os.getenv('EDDYPRO_PROJ_ID', 'ameriflux_pipeline')
    EDDYPRO_FILE_PROTOTYPE = os.getenv('EDDYPRO_FILE_PROTOTYPE', 'yyyy-mm-ddTHHMM??_Sorghum-00137.ghg')
    EDDYPRO_PROJ_FILE = os.getenv('EDDYPRO_PROJ_FILE', 'tests/data/2021-01-01T000000_Sorghum-00137.metadata')
    EDDYPRO_DYN_METADATA = os.getenv('EDDYPRO_DYN_METADATA', 'tests/data/Sorghum_2021_dynamic_metadata.csv')
    EDDYPRO_OUTPUT_PATH = os.getenv('EDDYPRO_OUTPUT_PATH', 'tests/data/test_output')
    EDDYPRO_INPUT_GHG_PATH = os.getenv('EDDYPRO_INPUT_GHG_PATH', 'tests/data/Raw Jan-Mar 2021 GHG Files')

    # PyFluxPro related data
    FULL_OUTPUT_PYFLUXPRO = os.getenv('FULL_OUTPUT_PYFLUXPRO', 'tests/data/full_output.csv')
    MET_DATA_30_PYFLUXPRO = os.getenv('MET_DATA_30_PYFLUXPRO', 'tests/data/Met_data_30.csv')
