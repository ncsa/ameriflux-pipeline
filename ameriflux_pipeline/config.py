# configs file
import os

class Config:
    '''
    class to list all configuration settings required for preprocessing and formatting
    '''
    MISSING_TIME = 96
    FULL_OUTPUT = os.path.join(os.getcwd(), "tests", "data",'eddypro_Sorghum_Jan1to7_2021_full_output_2021-11-03T083200_adv.csv')
    # inputs sheets for pyfluxpro renamed as per guide (PyFluxPro : Creating the database, step 1)
    FULL_OUTPUT_PYFLUXPRO = 'full_output.csv'
    MET_DATA_30_PYFLUXPRO = 'Met_data_30.csv'
