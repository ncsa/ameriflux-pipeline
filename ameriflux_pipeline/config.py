# configs file
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """
    class to list all configuration settings required for preprocessing and formatting for EddyPro and PyFluxPro
    """
    # obtaining ghg files using rsync
    # user confirmation to perform rsync
    SFTP_CONFIRMATION = os.getenv('SFTP_CONFIRMATION', 'N')
    SFTP_SERVER = os.getenv('SFTP_SERVER')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME')
    SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
    SFTP_GHG_REMOTE_PATH = os.getenv('SFTP_GHG_REMOTE_PATH')
    SFTP_GHG_LOCAL_PATH = os.getenv('SFTP_GHG_LOCAL_PATH')
    SFTP_MET_REMOTE_PATH = os.getenv('SFTP_MET_REMOTE_PATH')
    SFTP_MET_LOCAL_PATH = os.getenv('SFTP_MET_LOCAL_PATH')

    # input data to merge met data for specific time periods
    MERGE_FILES = os.getenv('MERGE_FILES', '')
    START_DATE = os.getenv('START_DATE', '')
    END_DATE = os.getenv('END_DATE', '')

    # input data for creating master meteorology data
    # input met data path
    INPUT_MET = os.getenv('INPUT_MET',
                          '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                          'master_met/input/FLUXSB_EC_JanMar2021.csv')
    # input precipitation data
    INPUT_PRECIP = os.getenv('INPUT_PRECIP',
                             '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                             'master_met/input/Precip_IWS_Jan-Feb_2021.xlsx')
    # Number of missing timeslot threshold for user confirmation to insert
    MISSING_TIME = os.getenv('MISSING_TIME', 96)
    # NOTE 9
    # User confirmation to insert large number of missing timestamps
    # Enter 'Y'/'YES' to insert, 'N'/'NO' to ignore and 'A'/'ASK' to await user input during runtime.
    MISSING_TIME_USER_CONFIRMATION = os.getenv('MISSING_TIME_USER_CONFIRMATION', 'Y')
    # master met output data path
    MASTER_MET = os.getenv('MASTER_MET',
                           '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                           'master_met/output/met_output.csv')

    # input data for formatting Eddypro master meteorology data.
    # input soil key data path
    INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY',
                               '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                               'eddypro/input/Soils_key.xlsx')

    # eddypro related parameters
    # bin folder location of eddypro_rp exec file
    EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC', '')  # '/Applications/eddypro.app/Contents/MacOS/bin'
    # EDDYPRO_PROJ_FILE_TEMPLATE
    EDDYPRO_PROJ_FILE_TEMPLATE = os.getenv('EDDYPRO_PROJ_FILE_TEMPLATE', '/Users/ameriflux-pipeline/ameriflux_pipeline/'
                                                                         'eddypro/templates/template.eddypro')
    # EddyPro run template
    EDDYPRO_PROJ_FILE_NAME = os.getenv('EDDYPRO_PROJ_FILE_NAME',
                                       '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                       'eddypro/templates/ameriflux.eddypro')
    EDDYPRO_PROJ_TITLE = os.getenv('EDDYPRO_PROJ_TITLE', 'AmeriFlux_Pipeline')
    EDDYPRO_PROJ_ID = os.getenv('EDDYPRO_PROJ_ID', 'ameriflux_pipeline')
    EDDYPRO_FILE_PROTOTYPE = os.getenv('EDDYPRO_FILE_PROTOTYPE', 'yyyy-mm-ddTHHMM??_Sorghum-00137.ghg')
    # EddyPro input metadata file from GHG
    EDDYPRO_PROJ_FILE = os.getenv('EDDYPRO_PROJ_FILE',
                                  '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                  'eddypro/input/2021-01-01T000000_Sorghum-00137.metadata')
    # EddyPro input dynamic metadata file
    EDDYPRO_DYN_METADATA = os.getenv('EDDYPRO_DYN_METADATA',
                                     '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                     'eddypro/input/Sorghum_2021_dynamic_metadata.csv')
    # EddyPro input GHG files folder
    EDDYPRO_INPUT_GHG_PATH = os.getenv('EDDYPRO_INPUT_GHG_PATH',
                                       '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                       'eddypro/input/ghg/')
    # EddyPro output folder
    EDDYPRO_OUTPUT_PATH = os.getenv('EDDYPRO_OUTPUT_PATH',
                                    '/Users/ameriflux-pipeline/ameriflux_pipeline/data/eddypro/output/')

    # PyFluxPro related data
    FULL_OUTPUT_PYFLUXPRO = os.getenv('FULL_OUTPUT_PYFLUXPRO',
                                      '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                      'generated/full_output.csv')
    MET_DATA_30_PYFLUXPRO = os.getenv('MET_DATA_30_PYFLUXPRO',
                                      '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                      'generated/Met_data_30.csv')
    PYFLUXPRO_INPUT_SHEET = os.getenv('PYFLUXPRO_INPUT_SHEET',
                                      '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                      'generated/pyfluxpro_input.xlsx')
    PYFLUXPRO_INPUT_AMERIFLUX = os.getenv('PYFLUXPRO_INPUT_AMERIFLUX',
                                          '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                          'generated/pyfluxpro_input_ameriflux.xlsx')
    # L1 Ameriflux Formatting
    L1_MAINSTEM_INPUT = os.getenv('L1_MAINSTEM_INPUT',
                                  '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/input/'
                                  'L1_mainstem.txt')
    L1_AMERIFLUX_ONLY_INPUT = os.getenv('L1_AMERIFLUX_ONLY_INPUT', '/Users/ameriflux-pipeline/ameriflux_pipeline/'
                                                                   'data/pyfluxpro/input/L1_ameriflux_only.txt')
    L1_AMERIFLUX_MAINSTEM_KEY = os.getenv('L1_AMERIFLUX_MAINSTEM_KEY',
                                          '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                          'input/Ameriflux-Mainstem-Key.xlsx')
    L1_AMERIFLUX_RUN_OUTPUT = os.getenv('L1_AMERIFLUX_RUN_OUTPUT',
                                        '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                        'generated/Sorghum_2021_L1.nc')
    L1_AMERIFLUX = os.getenv('L1_AMERIFLUX',
                             '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L1_ameriflux.txt')

    # User confirmation to replace erroring Ameriflux variable names in L1
    # Enter 'Y'/'YES' to replace, 'N'/'NO' to ignore and 'A'/'ASK' to await user input during runtime.
    AMERIFLUX_VARIABLE_USER_CONFIRMATION = os.getenv('AMERIFLUX_VARIABLE_USER_CONFIRMATION', 'N')
    L1_AMERIFLUX_ERRORING_VARIABLES_KEY = os.getenv('L1_AMERIFLUX_ERRORING_VARIABLES_KEY',
                                                    '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/'
                                                    'input/L1_erroring_variables.xlsx')

    # L2 Ameriflux Formatting
    L2_MAINSTEM_INPUT = os.getenv('L2_MAINSTEM_INPUT', '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                                       'pyfluxpro/input/L2_mainstem.txt')
    L2_AMERIFLUX_ONLY_INPUT = os.getenv('L2_AMERIFLUX_ONLY_INPUT', '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                                                   'pyfluxpro/input/L2_ameriflux_only.txt')
    L2_AMERIFLUX_RUN_OUTPUT = os.getenv('L2_AMERIFLUX_RUN_OUTPUT',
                                        '/Users/ameriflux-pipeline/ameriflux_pipeline/data/'
                                        'pyfluxpro/generated/Sorghum_2021_L2.nc')
    L2_AMERIFLUX = os.getenv('L2_AMERIFLUX',
                             '/Users/ameriflux-pipeline/ameriflux_pipeline/data/pyfluxpro/generated/L2_ameriflux.txt')

    # QA/QC values
    # precipitation threshold values used in creating Eddypro master meteorology data
    QC_PRECIP_LOWER = 0.0  # precipitation lower threshold value (inches)
    QC_PRECIP_UPPER = 0.2  # precipitation upper threshold value (inches)

    # Connect to dataserver
    SFTP_SERVER = os.getenv('SFTP_SERVER', '')
    SFTP_USERNAME = os.getenv('SFTP_USERNAME', '')
    SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', '')
