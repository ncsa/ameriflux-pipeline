# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made availabel under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is availabel at https://www.mozilla.org/en-US/MPL/2.0/

import os
import tkinter as tk

from tkinter import ttk as ttk
from tkinter import filedialog, messagebox
from dotenv import load_dotenv

from eddypro.runeddypro import RunEddypro


class EnvEditor():
    def __init__(self):
        # check what is the current platform
        self.OS_PLATFORM = RunEddypro.get_platform()

        # text variables
        self.SEPARATION_LABEL = "---------------------------------------------------------"
        self.SEPARATION_LABEL_SUB = "------------------"
        self.INFO_TITLE = "info"

        self.LINE_SFTP = 0
        # self.LINE_MISSING_TIME_USER_CONFIRMATION = 36
        self.LINE_EDDYPRO_FORMAT = 36
        self.LINE_EDDYPRO_RUN = 86
        self.LINE_PYFLUX_PRO = 141
        self.LINE_PYFLUX_L1 = 170
        self.LINE_SAVE_ENV = 217

        # ftp rsync variables
        self.SFTP_LABEL = " Sync files from the server"
        self.BROWSE_SFTP_CONFIRMATION = " User confirmation for syncing from the server"
        self.DESC_SFTP_CONFIRMATION = " user decision on whether to sync files from remote server"
        self.INFO_SFTP_CONFIRMATION = "When the answer is yes, the remote directory and local directory " \
                                      "with sync files."
        self.BROWSE_SFTP_SERVER = " Remote FTP Server URL"
        self.DESC_SFTP_SERVER = " URL of the remote FTP server"
        self.INFO_SFTP_SERVER = "The URL of the remote FTP server for connecting to local machine" \
                                " for syncing the local and remote directories."
        self.BROWSE_SFTP_USERNAME = " Username of the server"
        self.DESC_SFTP_USERNAME = " Username of the remote FTP server"
        self.INFO_SFTP_USERNAME = "Username that will be used for accessing the remote FTP server."
        self.BROWSE_SFTP_PASSWORD = " Password of the server"
        self.DESC_SFTP_PASSWORD = " Password of the remote FTP server"
        self.INFO_SFTP_PASSWORD = "Password that will be used for accessing the remote FTP server."
        self.BROWSE_SFTP_GHG_REMOTE_PATH = " Remote directory location for GHG files"
        self.DESC_SFTP_GHG_REMOTE_PATH = " Directory path for GHG files in the remote FTP server that will be synced"
        self.INFO_SFTP_GHG_REMOTE_PATH = "Directory path for GHG files in the remote FTP server. The files in the " \
                                         "directory will be synced to the local directory. "
        self.BROWSE_SFTP_GHG_LOCAL_PATH = " Local directory location for GHG files"
        self.DESC_SFTP_GHG_LOCAL_PATH = " Directory path for GHG files in the local machine that will be synced"
        self.INFO_SFTP_GHG_LOCAL_PATH = "Directory path for GHG files in the local machine. The files in the remote " \
                                        "directory will be synced here."
        self.BROWSE_SFTP_MET_REMOTE_PATH = " Remote directory location for MET files"
        self.DESC_SFTP_MET_REMOTE_PATH = " Directory path for MET files in the remote FTP server that will be synced"
        self.INFO_SFTP_MET_REMOTE_PATH = "Directory path for MET files in the remote FTP server. The files in the " \
                                         "directory will be synced to the local directory. "
        self.BROWSE_SFTP_MET_LOCAL_PATH = " Local directory location for MET files"
        self.DESC_SFTP_MET_LOCAL_PATH = " Directory path for MET files in the local machine that will be synced"
        self.INFO_SFTP_MET_LOCAL_PATH = "Directory path for MET files in the local machine. The files in the remote " \
                                        "directory will be synced here."

        # user confirmation variable
        self.MISSING_TIME_USER_CONFIRMATION_LABEL = " User confirmation"
        self.BROWSE_MISSING_TIME_USER_CONFIRAMTION = " Missing Timestamp Confirmation"
        self.DESC_MISSING_TIME_USER_CONFIRMATION = " user decision on whether to insert, ignore or ask during " \
                                                   "runtime in case of large number of missing timestamps"
        self.INFO_MISSING_TIME_USER_CONFIRMATION = "When the pipeline encounters a data gap, would you like it to " \
                                                   "(1) Y - insert empty time periods, " \
                                                   "(2) N - ignore the gap and return only time periods for which " \
                                                   "there is data, or " \
                                                   "(3) A - stop running and ask you? For (3), " \
                                                   "you can set the threshold for notification in \"Missing Time\". " \
                                                   "The choices will be asked only if the number of missing " \
                                                   "timestamps are bigger than missing timestamps thresholds"

        # eddypro fomatting variables
        self.EDDYPRO_FORMAT_VARIABLE = " Variables for EddyPro formatting"
        self.BROWSE_INPUT_MET = " Input Meteorology Data"
        self.DESC_INPUT_MET = " input meteorology data [DATA FILE]"
        self.INFO_INPUT_MET = "Raw meteorological data from the met tower datalogger. This will usually have a " \
                              ".dat extension originally but need to be converted to csv for the pipeline. Make sure " \
                              "the file you choose covers the time period you are interested in!"
        self.BROWSE_INPUT_PRECIP = " Input Precipitation Data"
        self.DESC_INPUT_PRECIP = " input precipitation data [DATA FILE]"
        self.INFO_INPUT_PRECIP = "Unformatted precipitation data from IWS in its native 5min resolution. " \
                                 "Will have column headers \"Date & Time (CST), Station, Precipitation (in.)\""
        self.BROWSE_MISSING_TIME = " Missing Time"
        self.DESC_MISSING_TIME = " number of missing 30 min periods allowed before user confirmation is required " \
                                 "to continue. [NUMBER]"
        self.INFO_MISSING_TIME = "How many missing time periods are you willing to tolerate before processing " \
                                 "stops to check in with you? This option exists to catch large gaps caused " \
                                 "by problems like missing files, allowing you to correct the problem before " \
                                 "restarting processing. Some options: 48 (1 day), 336 (1 week), 672 (2 weeks), " \
                                 "1440 (1 month)."
        self.BROWSE_MASTER_MET = " Master Meteorology Data"
        self.DESC_MASTER_MET = " output directory for formatted ‘master’ meteorology data (file will be " \
                               "auto-generated, only select the directory)[DIRECTORY]"
        self.INFO_MASTER_MET = "The directory where you want the automatically formatted \'master\' " \
                               "meteorological data to go"
        self.BROWSE_INPUT_SOIL_KEY = " Input Soil Key"
        self.DESC_INPUT_SOIL_KEY = " input soil key file [ANCILLARY FILE]"
        self.INFO_INPUT_SOIL_KEY = "This is an excel or sheets document with column names referencing site, " \
                                   "instrument, and “Datalogger”, “EddyPro” and “PyFluxPro” variable names. " \
                                   "It can be found at [bernacchi lab server address] or [sheets document URL]. " \
                                   "If soil sensors have changed recently, ensure that the key is accurate before " \
                                   "proceeding. "

        # eddypro running variables
        self.EDDYPRO_RUNNING_VARIABLE = " Variables for EddyPro running"
        self.BROWSE_EDDYPRO_BIN = " EddyPro Bin Folder"
        self.DESC_EDDYPRO_BIN = " location of eddypro bin directory [DIRECTORY]"
        self.INFO_EDDYPRO_BIN = "Location of the code that comes with (and runs) eddypro. Look for an actual " \
                                "directory named “bin”. This will usually be somewhere like " \
                                "C:\\Program Files\\LI-COR\\EddyPro-7.0.6\\bin"
        self.BROWSE_EDDYPRO_PROJ_TEMPLATE = " EddyPro Project Template File"
        self.DESC_EDDYPRO_PROJ_TEMPLATE = " file path for the eddypro project file template"
        self.INFO_EDDYPRO_PROJ_TEMPLATE = "This is a template EddyPro project file that will be used for creating " \
                                          "the EddyPro project file that saves the settings of an eddypro run. " \
                                          "Choose the eddypro template file. "
        self.BROWSE_EDDYPRO_PROJ_FILE_NAME = " EddyPro Project File"
        self.DESC_EDDYPRO_PROJ_FILE_NAME = " file path for the eddypro project file"
        self.INFO_EDDYPRO_PROJ_FILE_NAME = "The EddyPro project file saves the settings of an eddypro run. These are " \
                                           "useful if you ever want to go back and see what you did, " \
                                           "or share your processing specifications with someone else. " \
                                           "Choose where to save that here. "
        self.BROWSE_EDDYPRO_PROJ_TITLE = " EddyPro Project Title"
        self.DESC_EDDYPRO_PROJ_TITLE = " name of your eddypro project file [NAME]"
        self.INFO_EDDYPRO_PROJ_TITLE = "This will be the name of the eddypro project file (described in " \
                                       "\"EddyPro Project File Path\"). Choose something descriptive! This is NOT " \
                                       "the name that will be associated with the eddypro-processed output data " \
                                       "files; you will choose that in \"EddyPro Project ID\"."
        self.BROWSE_EDDYPRO_PROJ_ID = " EddyPro Project ID"
        self.DESC_EDDYPRO_PROJ_ID = " name of your eddypro project output[NAME]"
        self.INFO_EDDYPRO_PROJ_ID = "This will be the name tied to the output data files of your eddypro run. " \
                                    "Choose something descriptive!"
        self.BROWSE_EDDYPRO_FILE_PROTOTYPE = " EddyPro File Prototype"
        self.DESC_EDDYPRO_FILE_PROTOTYPE = " the form of the ghg file e.g, yyyy-mm-ddTHHMM??_Sorghum-00137.ghg"
        self.INFO_EDDYPRO_FILE_PROTOTYPE = "Eddypro can generate this automatically"
        self.BROWSE_EDDYPRO_PROJ_FILE = " EddyPro Metadata File from GHG File"
        self.DESC_EDDYPRO_PROJ_FILE = " IRGA (‘alternate’) metadata file [ANCILLARY FILE]"
        self.INFO_EDDYPRO_PROJ_FILE = "This is a file with extension .metadata, extracted from a ghg file. To get " \
                                      "this, unzip any ghg file included in this run. The result will be two files, " \
                                      "one of which has a .metadata extension. Delete the other unzipped file " \
                                      "(with extension ‘.data’) and move the .metadata file somewhere away from the " \
                                      "ghg files. Select it here. "
        self.BROWSE_EDDYPRO_DYN_METADATA = " EddyPro Dynamic Metadata"
        self.DESC_EDDYPRO_DYN_METADATA = " dynamic metadata file[ANCILLARY FILE]"
        self.INFO_EDDYPRO_DYN_METADATA = "This is a .csv containing instrument and canopy height changes. If you " \
                                         "don’t already have one for the time period included in this run, consult " \
                                         "the guide [guide location] for instructions to make one."
        self.BROWSE_EDDYPRO_OUTPUT_PATH = " EddyPro Output Path"
        self.DESC_EDDYPRO_OUTPUT_PATH = " output directory for eddypro data output [DIRECTORY]"
        self.INFO_EDDYPRO_OUTPUT_PATH = "The directory where you want your eddypro data output to go."
        self.BROWSE_EDDYPRO_INPUT_GHG_PATH = " EddyPro Input GHG Path"
        self.DESC_EDDYPRO_INPUT_GHG_PATH = " directory for input ghg data [DIRECTORY]"
        self.INFO_EDDYPRO_INPUT_GHG_PATH = "A directory with (usually many) .ghg files. You may have to unzip up " \
                                           "to twice to get to files with the .ghg extension. All the .ghg files " \
                                           "should be in one big pile, without dividing folders. Consult the guide " \
                                           "or flux project manager if you need server access or other help. "

        # PyFluxPro related data
        self.PYFLUXPROPRO_RUNNING_VARIABLE = " Variables for PyFluxPro running"
        self.BROWSE_FULL_OUTPUT_PYFLUXPRO = " PyFluxPro Full Output (select folder)"
        self.DESC_FULL_OUTPUT_PYFLUXPRO = " output directory for eddypro \'full_output\' data file (file will " \
                                          "be auto-generated, only select the directory) [DIRECTORY]"
        self.INFO_FULL_OUTPUT_PYFLUXPRO = "The directory where you want eddypro’s full_output file " \
                                          "(used in PyFluxPro)to go. "
        self.BROWSE_MET_DATA_30_PYFLUXPRO = " PyFluxPro Met Data 30 Output (select folder)"
        self.DESC_MET_DATA_30_PYFLUXPRO = " output directory for processed \'Met_data_30\' data file (file will be " \
                                          "auto-generated, only select the directory)[DIRECTORY]"
        self.INFO_MET_DATA_30_PYFLUXPRO = "The directory where you want formatted met data (used in PyFluxPro) to go."
        self.BROWSE_PYFLUXPRO_INPUT_SHEET = " PyFluxPro Input Sheet File"
        self.DESC_PYFLUXPRO_INPUT_SHEET = " file for pyfluxpro input sheet combining full output and met data 30"
        self.INFO_PYFLUXPRO_INPUT_SHEET = "The excel file where you want the fully-processed PyFluxPro input file " \
                                          "to go."
        self.BROWSE_PYFLUXPRO_INPUT_AMERIFLUX = " PyFluxPro input excel sheet with Ameriflux formatting"
        self.DESC_PYFLUXPRO_INPUT_AMERIFLUX = " output file for pyflux pro input excel file with AmeriFlux formatting"
        self.INFO_PYFLUXPRO_INPUT_AMERIFLUX = "The excel file that has the identical content as PyFluxPro input " \
                                              "excel file with variable naming convention accepted by AmeriFlux."

        # PyFluxPro L1 related data
        self.PYFLUXPROPRO_L1_VARIABLE = " Variables for PyFluxPro AmeriFlux formatting"
        self.BROWSE_AMERIFLUX_VARIABLE_USER_CONFIRMATION = " User decision on erroring variable names in PyFlux Pro L1"
        self.DESC_AMERIFLUX_VARIABLE_USER_CONFIRMATION = " User decision on handling erroring variable names in " \
                                                         "PyFluxPro L1."
        self.INFO_AMERIFLUX_VARIABLE_USER_CONFIRMATION = "User decision on whether to replace, ignore or ask during " \
                                                         "runtime in case of erroring variable names in PyFluxPro L1."
        self.BROWSE_L1_MAINSTEM_INPUT = " PyFluxPro L1.txt file"
        self.DESC_L1_MAINSTEM_INPUT = " filename for L1 control file for mainstem variables"
        self.INFO_L1_MAINSTEM_INPUT = "PyFluxpro input L1 control file for mainstem variables"
        self.BROWSE_L1_AMERIFLUX_ONLY_INPUT = " L1.txt file formatted for AmeriFlux"
        self.DESC_L1_AMERIFLUX_ONLY_INPUT = " PyFluxpro input L1 control file for ameriflux-only variables."
        self.INFO_L1_AMERIFLUX_ONLY_INPUT = "The txt file needed by the process with AmeriFlux " \
                                            "specific formatting for PyFluxPro's L1 process."
        self.BROWSE_L1_AMERIFLUX_MAINSTEM_KEY = " L1 file's variable matching key excel File"
        self.DESC_L1_AMERIFLUX_MAINSTEM_KEY = " key file for converting L1 file's variables for AmeriFlux formatting."
        self.INFO_L1_AMERIFLUX_MAINSTEM_KEY = "Variable name mapping from PyFluxPro friendly names to Ameriflux " \
                                              "friendly names. This is an excel sheet containing all the variables " \
                                              "to be included in L1_AMERIFLUX with name changes and unit changes " \
                                              "when necessary."
        self.BROWSE_L1_AMERIFLUX_RUN_OUTPUT = " L1 output nc file name that will be generated"
        self.DESC_L1_AMERIFLUX_RUN_OUTPUT = " output .nc file that will be generated after PyFluxPro L1 run " \
                                            "with AmeriFlux format."
        self.INFO_L1_AMERIFLUX_RUN_OUTPUT = "The outfile that is to be written after PyFluxPro L1 run with " \
                                            "AmeriFlux L1 control file. This is to be present in the out_filename " \
                                            "info in L1."
        self.BROWSE_L1_AMERIFLUX = " L1 output txt file name with AmeriFlux standards "
        self.DESC_L1_AMERIFLUX = " L1 control file generated as per AmeriFlux friendly variables."
        self.INFO_L1_AMERIFLUX = "The output L1 control txt file that has the format with AmeriFlux friendly " \
                                 "variable names."
        self.BROWSE_L1_AMERIFLUX_ERRORING_VARIABLES_KEY = " Erroring variable key file for AmeriFlux variables"
        self.DESC_L1_AMERIFLUX_ERRORING_VARIABLES_KEY = " Variable name key file for matching the original variable " \
                                                        "names to AmeriFlux names"
        self.INFO_L1_AMERIFLUX_ERRORING_VARIABLES_KEY = "Variable name key used to match the original variable names " \
                                                        "to AmeriFlux names for variables throwing an error " \
                                                        "in PyFluxPro L1."

        # PyFluxPro L2 related data
        self.BROWSE_L2_MAINSTEM_INPUT = " PyFluxPro L2.txt file"
        self.DESC_L2_MAINSTEM_INPUT = " filename for L2 control file for mainstem variables"
        self.INFO_L2_MAINSTEM_INPUT = "PyFluxpro input L2 control file for mainstem variables"
        self.BROWSE_L2_AMERIFLUX_ONLY_INPUT = " L2.txt file formatted for AmeriFlux"
        self.DESC_L2_AMERIFLUX_ONLY_INPUT = " PyFluxpro input L2 control file for ameriflux-only variables."
        self.INFO_L2_AMERIFLUX_ONLY_INPUT = "The txt file needed by the process with AmeriFlux specific " \
                                            "formatting for PyFluxPro's L2 process."
        self.BROWSE_L2_AMERIFLUX_RUN_OUTPUT = " L2 output nc file name that will be generated"
        self.DESC_L2_AMERIFLUX_RUN_OUTPUT = " output .nc file that will be generated after PyFluxPro L2 run " \
                                            "with AmeriFlux format."
        self.INFO_L2_AMERIFLUX_RUN_OUTPUT = "The outfile that is to be written after PyFluxPro L2 run with " \
                                            "AmeriFlux L2 control file. This is to be present in the out_filename " \
                                            "info in L2."
        self.BROWSE_L2_AMERIFLUX = " L2 output txt file name with AmeriFlux standards"
        self.DESC_L2_AMERIFLUX = " L2 control file generated as per AmeriFlux friendly variables."
        self.INFO_L2_AMERIFLUX = "The output L2 control txt file that has the format with AmeriFlux friendly " \
                                 "variable names."

        # save
        self.SAVE_LABEL = "Save .env file"
        self.SAVE_ENV_FILE = "Save"

        # font variables
        self.MAIN_BOLD_FONT = "Times 14 bold"
        self.MAIN_FONT = "Times 11"
        self.BOLD_FONT = "Times 11 bold"
        self.DESC_FONT = "Times 10 italic"

        # Load .env file
        load_dotenv()

        self.SFTP_CONFIRMATION = os.getenv('SFTP_CONFIRMATION')
        self.SFTP_SERVER = os.getenv('SFTP_SERVER')
        self.SFTP_USERNAME = os.getenv('SFTP_USERNAME')
        self.SFTP_PASSWORD = os.getenv('SFTP_PASSWORD')
        self.SFTP_GHG_REMOTE_PATH = os.getenv('SFTP_GHG_REMOTE_PATH')
        self.SFTP_GHG_LOCAL_PATH = os.getenv('SFTP_GHG_LOCAL_PATH')
        self.SFTP_MET_REMOTE_PATH = os.getenv('SFTP_MET_REMOTE_PATH')
        self.SFTP_MET_LOCAL_PATH = os.getenv('SFTP_MET_LOCAL_PATH')

        self.MISSING_TIME_USER_CONFIRMATION = os.getenv('MISSING_TIME_USER_CONFIRMATION')

        self.INPUT_MET = os.getenv('INPUT_MET')
        self.INPUT_PRECIP = os.getenv('INPUT_PRECIP')
        self.MISSING_TIME = os.getenv('MISSING_TIME')
        self.MASTER_MET = os.getenv('MASTER_MET')
        self.INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY')

        self.EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC')
        self.EDDYPRO_PROJ_FILE_TEMPLATE = os.getenv('EDDYPRO_PROJ_FILE_TEMPLATE')
        self.EDDYPRO_PROJ_FILE_NAME = os.getenv('EDDYPRO_PROJ_FILE_NAME')
        self.EDDYPRO_PROJ_TITLE = os.getenv('EDDYPRO_PROJ_TITLE')
        self.EDDYPRO_PROJ_ID = os.getenv('EDDYPRO_PROJ_ID')
        self.EDDYPRO_FILE_PROTOTYPE = os.getenv('EDDYPRO_FILE_PROTOTYPE')
        self.EDDYPRO_PROJ_FILE = os.getenv('EDDYPRO_PROJ_FILE')
        self.EDDYPRO_DYN_METADATA = os.getenv('EDDYPRO_DYN_METADATA')
        self.EDDYPRO_OUTPUT_PATH = os.getenv('EDDYPRO_OUTPUT_PATH')
        self.EDDYPRO_INPUT_GHG_PATH = os.getenv('EDDYPRO_INPUT_GHG_PATH')

        self.FULL_OUTPUT_PYFLUXPRO = os.getenv('FULL_OUTPUT_PYFLUXPRO')
        self.MET_DATA_30_PYFLUXPRO = os.getenv('MET_DATA_30_PYFLUXPRO')
        self.PYFLUXPRO_INPUT_SHEET = os.getenv('PYFLUXPRO_INPUT_SHEET')
        self.PYFLUXPRO_INPUT_AMERIFLUX = os.getenv('PYFLUXPRO_INPUT_AMERIFLUX')

        self.AMERIFLUX_VARIABLE_USER_CONFIRMATION = os.getenv('AMERIFLUX_VARIABLE_USER_CONFIRMATION')
        self.L1_MAINSTEM_INPUT = os.getenv('L1_MAINSTEM_INPUT')
        self.L1_AMERIFLUX_ONLY_INPUT = os.getenv('L1_AMERIFLUX_ONLY_INPUT')
        self.L1_AMERIFLUX_MAINSTEM_KEY = os.getenv('L1_AMERIFLUX_MAINSTEM_KEY')
        self.L1_AMERIFLUX_RUN_OUTPUT = os.getenv('L1_AMERIFLUX_RUN_OUTPUT')
        self.L1_AMERIFLUX = os.getenv('L1_AMERIFLUX')
        self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY = os.getenv('L1_AMERIFLUX_ERRORING_VARIABLES_KEY')
        self.L2_MAINSTEM_INPUT = os.getenv('L2_MAINSTEM_INPUT')
        self.L2_AMERIFLUX_ONLY_INPUT = os.getenv('L2_AMERIFLUX_ONLY_INPUT')
        self.L2_AMERIFLUX_RUN_OUTPUT = os.getenv('L2_AMERIFLUX_RUN_OUTPUT')
        self.L2_AMERIFLUX = os.getenv('L2_AMERIFLUX')

        self.run()

    def run(self):
        # check if there is .env file
        # checking this by SFTP_CONFIRMATION variable is not none
        is_env = os.path.exists('.env')

        # if .env doesn't exist, pre fill the values
        if not is_env:
            print("There is no .env file. The GUI will fill default values. "
                  "Please make sure if every values are correct.")

            self.preset_variables()

        # create main gui window
        root = tk.Tk()
        root.title("AmeriFlux Pipeline Environment Setter")
        root.geometry("800x400")

        # create a main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        # create a frame for X scrollbar
        sec = tk.Frame(main_frame)
        sec.pack(fill=tk.X, side=tk.BOTTOM)

        # create a canvas
        self.main_canvas = tk.Canvas(main_frame)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # add a scrollbar to the canvas
        x_scrollbar = ttk.Scrollbar(sec, orient=tk.HORIZONTAL, command=self.main_canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.main_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # configure the canvas
        self.main_canvas.configure(xscrollcommand=x_scrollbar.set)
        self.main_canvas.configure(yscrollcommand=y_scrollbar.set)
        self.main_canvas.bind('<Configure>',
                              lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # create another frame inside the canvas
        second_frame = tk.Frame(self.main_canvas)

        # add that new frame to a window in the canvas
        self.main_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        ########################################################
        ########################################################
        ########################################################
        i = self.LINE_SFTP
        # create user confirmation
        label_sftp_confirm = tk.Label(second_frame, text=self.SFTP_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i, columnspan=3)
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+1, columnspan=3)
        browse_sftp_confirm = tk.Label(second_frame, text=self.BROWSE_SFTP_CONFIRMATION, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+2, column=0)
        button_sftp_confirm = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_confirm). \
            grid(sticky="w", row=i+2, column=1)
        desc_sftp_confirm = tk.Label(second_frame, text=self.DESC_SFTP_CONFIRMATION, font=self.DESC_FONT). \
            grid(sticky="w", row=i+3, columnspan=3)
        confirm_sftp_list = ("Y", "N")
        confirm_sftp_list_index = 0
        for index, value in enumerate(confirm_sftp_list):
            if value == self.SFTP_CONFIRMATION:
                confirm_sftp_list_index = index
        # n = tk.StringVar()
        self.combo_sftp_confirm = ttk.Combobox(second_frame)
        self.combo_sftp_confirm['values'] = confirm_sftp_list
        self.combo_sftp_confirm.current(confirm_sftp_list_index)
        self.combo_sftp_confirm.grid(sticky="w", row=i + 4, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+5, column=0, columnspan=3)

        # create sftp server url
        label_sftp_server = tk.Label(master=second_frame, text=self.BROWSE_SFTP_SERVER, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+6, column=0)
        info_sftp_server = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_server). \
            grid(sticky="w", row=i+6, column=1, columnspan=2)
        desc_sftp_server = tk.Label(second_frame, text=self.DESC_SFTP_SERVER, font=self.DESC_FONT). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)
        self.sftp_server = tk.Entry(master=second_frame, width=40, font=self.MAIN_FONT)
        if self.SFTP_SERVER is not None:
            self.sftp_server.insert(0, self.SFTP_SERVER)
        self.sftp_server.grid(sticky="w", row=i+8, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+9, column=0, columnspan=3)

        # create sftp username
        label_sftp_username = tk.Label(master=second_frame, text=self.BROWSE_SFTP_USERNAME, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+10, column=0)
        info_sftp_username = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_username). \
            grid(sticky="w", row=i+10, column=1, columnspan=2)
        desc_sftp_username = tk.Label(second_frame, text=self.DESC_SFTP_USERNAME, font=self.DESC_FONT). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)
        self.sftp_username = tk.Entry(master=second_frame, width=20, font=self.MAIN_FONT)
        if self.SFTP_USERNAME is not None:
            self.sftp_username.insert(0, self.SFTP_USERNAME)
        self.sftp_username.grid(sticky="w", row=i+12, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+13, column=0, columnspan=3)

        # create sftp password
        label_sftp_password = tk.Label(master=second_frame, text=self.BROWSE_SFTP_PASSWORD, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+14, column=0)
        info_sftp_password = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_password). \
            grid(sticky="w", row=i+14, column=1, columnspan=2)
        desc_sftp_password = tk.Label(second_frame, text=self.DESC_SFTP_PASSWORD, font=self.DESC_FONT). \
            grid(sticky="w", row=i+15, column=0, columnspan=3)
        self.sftp_password = tk.Entry(master=second_frame, width=20, font=self.MAIN_FONT, show="*")
        if self.SFTP_PASSWORD is not None:
            self.sftp_password.insert(0, self.SFTP_PASSWORD)
        self.sftp_password.grid(sticky="w", row=i+16, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+17, column=0, columnspan=3)

        # create sftp ghg remote path
        label_ftp_ghg_remote_path = tk.Label(
            master=second_frame, text=self.BROWSE_SFTP_GHG_REMOTE_PATH, font=self.BOLD_FONT).\
            grid(sticky="w", row=i+18, column=0)
        info_sftp_ghg_remote_path = tk.Button(
            second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_ghg_remote_path).\
            grid(sticky="w", row=i+18, column=1, columnspan=2)
        desc_sftp_ghg_remote_path = tk.Label(
            second_frame, text=self.DESC_SFTP_GHG_REMOTE_PATH, font=self.DESC_FONT).\
            grid(sticky="w", row=i+19, column=0, columnspan=3)
        self.sftp_ghg_remote_path = tk.Entry(master=second_frame, width=60, font=self.MAIN_FONT)
        if self.SFTP_GHG_REMOTE_PATH is not None:
            self.sftp_ghg_remote_path.insert(0, self.SFTP_GHG_REMOTE_PATH)
        self.sftp_ghg_remote_path.grid(sticky="w", row=i+20, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+21, column=0, columnspan=3)

        # create sftp ghg local path
        label_sftp_ghg_local_path = tk.Label(
            master=second_frame, text=self.BROWSE_SFTP_GHG_LOCAL_PATH, font=self.BOLD_FONT).\
            grid(sticky="w", row=i+22, column=0)
        button_sftp_ghg_local_path = tk.Button(
            second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_ghg_local_path).\
            grid(sticky="w", row=i+22, column=1)
        button_sftp_ghg_local_path = tk.Button(
            master=second_frame, text="Browse", font=self.MAIN_FONT, command=self.browse_sftp_ghg_local_path).\
            grid(sticky="w", row=i+22, column=2)
        desc_sftp_ghg_local_path = tk.Label(
            second_frame, text=self.DESC_SFTP_GHG_LOCAL_PATH, font=self.DESC_FONT).\
            grid(sticky="w", row=i+23, column=0, columnspan=3)
        self.path_sftp_ghg_local_path = tk.Label(
            master=second_frame, text=self.SFTP_GHG_LOCAL_PATH, font=self.MAIN_FONT)
        self.path_sftp_ghg_local_path.grid(sticky="w", row=i + 24, column=0, columnspan=3)
        label_separation = tk.Label(
            master=second_frame, text=self.SEPARATION_LABEL_SUB).\
            grid(sticky="w", row=i+25, column=0, columnspan=3)

        # create sftp met remote path
        label_ftp_met_remote_path = tk.Label(
            master=second_frame, text=self.BROWSE_SFTP_MET_REMOTE_PATH, font=self.BOLD_FONT).\
            grid(sticky="w", row=i+26, column=0)
        info_sftp_met_remote_path = tk.Button(
            second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_met_remote_path).\
            grid(sticky="w", row=i+26, column=1, columnspan=2)
        desc_sftp_met_remote_path = tk.Label(
            second_frame, text=self.DESC_SFTP_MET_REMOTE_PATH, font=self.DESC_FONT).\
            grid(sticky="w", row=i+27, column=0, columnspan=3)
        self.sftp_met_remote_path = tk.Entry(master=second_frame, width=60, font=self.MAIN_FONT)
        if self.SFTP_MET_REMOTE_PATH is not None:
            self.sftp_met_remote_path.insert(0, self.SFTP_MET_REMOTE_PATH)
        self.sftp_met_remote_path.grid(sticky="w", row=i+28, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB).\
            grid(sticky="w", row=i+29, column=0, columnspan=3)

        # create sftp met local path
        label_sftp_met_local_path = tk.Label(
            master=second_frame, text=self.BROWSE_SFTP_MET_LOCAL_PATH, font=self.BOLD_FONT).\
            grid(sticky="w", row=i+30, column=0)
        button_sftp_met_local_path = tk.Button(
            second_frame, text=self.INFO_TITLE, command=self.on_click_sftp_met_local_path).\
            grid(sticky="w", row=i+30, column=1)
        button_sftp_met_local_path = tk.Button(
            master=second_frame, text="Browse", font=self.MAIN_FONT, command=self.browse_sftp_met_local_path). \
            grid(sticky="w", row=i+30, column=2)
        desc_sftp_met_local_path = tk.Label(
            second_frame, text=self.DESC_SFTP_MET_LOCAL_PATH, font=self.DESC_FONT).\
            grid(sticky="w", row=i+31, column=0, columnspan=3)
        self.path_sftp_met_local_path = tk.Label(
            master=second_frame, text=self.SFTP_MET_LOCAL_PATH, font=self.MAIN_FONT)
        self.path_sftp_met_local_path.grid(sticky="w", row=i + 32, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+33, column=0, columnspan=3)

        # ########################################################
        # i = self.LINE_MISSING_TIME_USER_CONFIRMATION
        # # create user confirmation
        # label_user_confirm = tk.Label(
        #     second_frame, text=self.MISSING_TIME_USER_CONFIRMATION_LABEL, font=self.MAIN_BOLD_FONT). \
        #     grid(sticky="w", row=i, columnspan=3)
        # label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+1, columnspan=3)
        # browse_user_confirm = tk.Label(
        #     second_frame, text=self.BROWSE_MISSING_TIME_USER_CONFIRAMTION, font=self.BOLD_FONT). \
        #     grid(sticky="w", row=i+2, column=0)
        # button_uesr_confirm = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_user_confirm).\
        #     grid(sticky="w", row=i+2, column=1)
        # desc_user_confirm = tk.Label(
        #     second_frame, text=self.DESC_MISSING_TIME_USER_CONFIRMATION, font=self.DESC_FONT).\
        #     grid(sticky="w", row=i+3, columnspan=3)
        # confirm_list = ("Y", "N", "A")
        # confirm_list_index = 0
        # for index, value in enumerate(confirm_list):
        #     if value == self.MISSING_TIME_USER_CONFIRMATION:
        #         confirm_list_index = index
        # # n = tk.StringVar()
        # self.combo_confirm = ttk.Combobox(second_frame)
        # self.combo_confirm['values'] = confirm_list
        # self.combo_confirm.current(confirm_list_index)
        # self.combo_confirm.grid(sticky="w", row=i+4, columnspan=3)

        #############################################################
        i = self.LINE_EDDYPRO_FORMAT
        # create eddypro format main label
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, columnspan=3)
        label_eddypro_format = tk.Label(master=second_frame, text=self.EDDYPRO_FORMAT_VARIABLE,
                                        font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+2, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL).\
            grid(sticky="w", row=i+3, columnspan=3)

        # create missing time user confirmation box
        browse_user_confirm = tk.Label(
            second_frame, text=self.BROWSE_MISSING_TIME_USER_CONFIRAMTION, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+4, column=0)
        button_uesr_confirm = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_user_confirm). \
            grid(sticky="w", row=i+4, column=1)
        desc_user_confirm = tk.Label(
            second_frame, text=self.DESC_MISSING_TIME_USER_CONFIRMATION, font=self.DESC_FONT). \
            grid(sticky="w", row=i+5, columnspan=3)
        confirm_list = ("Y", "N", "A")
        confirm_list_index = 0
        for index, value in enumerate(confirm_list):
            if value == self.MISSING_TIME_USER_CONFIRMATION:
                confirm_list_index = index
        # n = tk.StringVar()
        self.combo_confirm = ttk.Combobox(second_frame)
        self.combo_confirm['values'] = confirm_list
        self.combo_confirm.current(confirm_list_index)
        self.combo_confirm.grid(sticky="w", row=i+6, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)

        # create eddypro format input meteorology data
        label_input_met = tk.Label(master=second_frame, text=self.BROWSE_INPUT_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+8, column=0)
        button_info_input_met = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_input_met). \
            grid(sticky="w", row=i+8, column=1)
        button_browse_input_met = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                            command=self.browse_input_met). \
            grid(sticky="w", row=i+8, column=2)
        desc_input_met = tk.Label(second_frame, text=self.DESC_INPUT_MET, font=self.DESC_FONT).\
            grid(sticky="w", row=i+9, column=0, columnspan=3)
        self.path_input_met = tk.Label(master=second_frame, text=self.INPUT_MET, font=self.MAIN_FONT)
        self.path_input_met.grid(sticky="w", row=i+10, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)

        # create eddypro format input precipitation data
        label_input_precip = tk.Label(master=second_frame, text=self.BROWSE_INPUT_PRECIP, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+12, column=0)
        button_info_input_precip = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_input_precip). \
            grid(sticky="w", row=i+12, column=1)
        button_browse_input_precip = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                               command=self.browse_input_precip). \
            grid(sticky="w", row=i+12, column=2)
        desc_input_precip = tk.Label(second_frame, text=self.DESC_INPUT_PRECIP, font=self.DESC_FONT).\
            grid(sticky="w", row=i+13, column=0, columnspan=3)
        self.path_input_precip = tk.Label(master=second_frame, text=self.INPUT_PRECIP, font=self.MAIN_FONT)
        self.path_input_precip.grid(sticky="w", row=i+14, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+15, column=0, columnspan=3)

        # create eddypro format missing time
        missing_time_label = tk.Label(master=second_frame, text="Missing Time", font=self.BOLD_FONT). \
            grid(sticky="w", row=i+16, column=0)
        button_info_missing_time = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_missing_time).\
            grid(sticky="w", row=i+16, column=1, columnspan=2)
        desc_missing_time = tk.Label(second_frame, text=self.DESC_MISSING_TIME, font=self.DESC_FONT).\
            grid(sticky="w", row=i+17, column=0, columnspan=3)
        self.missing_time = tk.Entry(master=second_frame, width=10, font=self.MAIN_FONT)
        if self.MISSING_TIME is not None:
            self.missing_time.insert(0, self.MISSING_TIME)
        self.missing_time.grid(sticky="w", row=i+18, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+19, column=0, columnspan=3)

        # create eddypro format master met
        label_master_met = tk.Label(master=second_frame, text=self.BROWSE_MASTER_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+20, column=0)
        button_info_master_met = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_master_met).\
            grid(sticky="w", row=i+20, column=1)
        button_browse_input_master_met = tk.Button(master=second_frame, text="Browse",
                                                   font=self.MAIN_FONT, command=self.browse_master_met). \
            grid(sticky="w", row=i+20, column=2)
        desc_master_met = tk.Label(second_frame, text=self.DESC_MASTER_MET, font=self.DESC_FONT).\
            grid(sticky="w", row=i+21, column=0, columnspan=2)
        self.path_master_met = tk.Label(master=second_frame, text=self.MASTER_MET, font=self.MAIN_FONT)
        self.path_master_met.grid(sticky="w", row=i+22, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+23, column=0, columnspan=3)

        # create eddypro format input soil key
        label_soil_key = tk.Label(master=second_frame, text=self.BROWSE_INPUT_SOIL_KEY, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+24, column=0)
        button_info_soil_key = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_soil_key).\
            grid(sticky="w", row=i+24, column=1)
        button_browse_input_soil_key = tk.Button(master=second_frame, text="Browse",
                                                 font=self.MAIN_FONT, command=self.browse_input_soil_key). \
            grid(sticky="w", row=i+24, column=2)
        desc_input_soil_key = tk.Label(second_frame, text=self.DESC_INPUT_SOIL_KEY, font=self.DESC_FONT).\
            grid(sticky="w", row=i+25, column=0, columnspan=2)
        self.path_input_soil_key = tk.Label(master=second_frame, text=self.INPUT_SOIL_KEY, font=self.MAIN_FONT)
        self.path_input_soil_key.grid(sticky="w", row=i+26, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+27, column=0, columnspan=3)

        #############################################################
        # create eddypro run main title
        i = self.LINE_EDDYPRO_RUN
        label_separation = tk.Label(master=second_frame, text=""). \
            grid(sticky="w", row=i, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=""). \
            grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_eddypro_run = tk.Label(master=second_frame, text=self.EDDYPRO_RUNNING_VARIABLE,
                                     font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+2, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+3, column=0, columnspan=3)

        # create eddypro bin location
        label_eddypro_bin = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_BIN, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+4, column=0)
        info_eddypro_bin = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                     command=self.on_click_eddypro_bin).grid(sticky="w", row=i+4, column=1)
        button_browse_eddypro_bin = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                              command=self.browse_eddypro_bin). \
            grid(sticky="w", row=i+4, column=2)
        desc_eddypro_bin = tk.Label(second_frame, text=self.DESC_EDDYPRO_BIN, font=self.DESC_FONT).\
            grid(sticky="w", row=i+5, column=0, columnspan=2)
        self.path_eddypro_bin = tk.Label(master=second_frame, text=self.EDDYPRO_BIN_LOC, font=self.MAIN_FONT)
        self.path_eddypro_bin.grid(sticky="w", row=i+6, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)

        # create eddypro project template file
        label_eddypro_proj_template = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_TEMPLATE,
                                               font=self.BOLD_FONT).grid(sticky="w", row=i+8, column=0)
        info_eddypro_proj_template = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                               command=self.on_click_eddypro_proj_template). \
            grid(sticky="w", row=i+8, column=1)
        button_browse_eddypro_proj_template = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_proj_template).grid(sticky="w", row=i+8, column=2)
        desc_eddypro_proj_template = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROJ_TEMPLATE,
                                              font=self.DESC_FONT).grid(sticky="w", row=i+9, column=0, columnspan=3)
        self.path_eddypro_proj_template = \
            tk.Label(master=second_frame, text=self.EDDYPRO_PROJ_FILE_TEMPLATE, font=self.MAIN_FONT)
        self.path_eddypro_proj_template.grid(sticky="w", row=i+10, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)

        # create eddypro project file
        label_eddypro_proj_file_name = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_FILE_NAME,
                                                font=self.BOLD_FONT).grid(sticky="w", row=i+12, column=0)
        info_eddypro_proj_file_name = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                command=self.on_click_eddypro_proj_file_name). \
            grid(sticky="w", row=i+12, column=1)
        button_browse_eddypro_proj_file_name = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_proj_file_name).grid(sticky="w", row=i+12, column=2)
        desc_eddypro_proj_file_name = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROJ_FILE_NAME,
                                               font=self.DESC_FONT).grid(sticky="w", row=i+13, column=0, columnspan=3)
        self.path_eddypro_proj_file_name = \
            tk.Label(master=second_frame, text=self.EDDYPRO_PROJ_FILE_NAME, font=self.MAIN_FONT)
        self.path_eddypro_proj_file_name.grid(sticky="w", row=i+14, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+15, column=0, columnspan=3)

        # create eddypro project title
        eddypro_proj_title_label = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_TITLE,
                                            font=self.BOLD_FONT).grid(sticky="w", row=i+16, column=0)
        info_eddypro_proj_title = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                            command=self.on_click_eddypro_proj_title).\
            grid(sticky="w", row=i+16, column=1, columnspan=2)
        desc_eddypro_proj_title = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROJ_TITLE, font=self.DESC_FONT).\
            grid(sticky="w", row=i+17, column=0, columnspan=3)
        self.eddypro_proj_title = tk.Entry(master=second_frame, width=50, font=self.MAIN_FONT)
        if self.EDDYPRO_PROJ_TITLE is not None:
            self.eddypro_proj_title.insert(0, self.EDDYPRO_PROJ_TITLE)
        self.eddypro_proj_title.grid(sticky="w", row=i+18, column=0, columnspan=3)
        label_separation = \
            tk.Label(master=second_frame,
                     text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+19, column=0, columnspan=3)

        # create eddypro project id
        eddypro_proj_id_label = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_ID, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+20, column=0, columnspan=3)
        info_eddypro_proj_id = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                         command=self.on_click_eddypro_proj_id).\
            grid(sticky="w", row=i+20, column=1, columnspan=2)
        desc_eddypro_proj_id = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROJ_ID, font=self.DESC_FONT).\
            grid(sticky="w", row=i+21, column=0, columnspan=3)
        self.eddypro_proj_id = tk.Entry(master=second_frame, width=50, font=self.MAIN_FONT)
        if self.EDDYPRO_PROJ_ID is not None:
            self.eddypro_proj_id.insert(0, self.EDDYPRO_PROJ_ID)
        self.eddypro_proj_id.grid(sticky="w", row=i+22, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+23, column=0, columnspan=3)

        # create eddypro file prototype
        eddypro_file_prototype_label = \
            tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_FILE_PROTOTYPE,
                     font=self.BOLD_FONT).grid(sticky="w", row=i+24, column=0)
        info_eddypro_file_prototype = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                command=self.on_click_eddypro_file_prototype).\
            grid(sticky="w", row=i+24, column=1, columnspan=2)
        desc_eddypro_file_prototype = tk.Label(second_frame, text=self.DESC_EDDYPRO_FILE_PROTOTYPE,
                                               font=self.DESC_FONT).grid(sticky="w", row=i+25, column=0, columnspan=3)
        self.eddypro_file_prototype = tk.Entry(master=second_frame, width=i+26, font=self.MAIN_FONT)
        if self.EDDYPRO_FILE_PROTOTYPE is not None:
            self.eddypro_file_prototype.insert(0, self.EDDYPRO_FILE_PROTOTYPE)
        self.eddypro_file_prototype.grid(sticky="w", row=i+27, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+28, column=0, columnspan=3)

        # create eddypro proj file that is metadata
        label_eddypro_proj_file = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_FILE,
                                           font=self.BOLD_FONT).grid(sticky="w", row=i+29, column=0)
        info_eddypro_proj_file = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                           command=self.on_click_eddypro_proj_file).\
            grid(sticky="w", row=i+29, column=1)
        button_browse_eddypro_proj_file = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                                    command=self.browse_eddypro_proj_file).\
            grid(sticky="w", row=i+29, column=2, columnspan=2)
        desc_eddypro_proj_file = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROJ_FILE, font=self.DESC_FONT).\
            grid(sticky="w", row=i+30, column=0, columnspan=3)
        self.path_eddypro_proj_file = tk.Label(master=second_frame, text=self.EDDYPRO_PROJ_FILE, font=self.MAIN_FONT)
        self.path_eddypro_proj_file.grid(sticky="w", row=i+31, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+32, column=0, columnspan=3)

        # create eddypro dynamic metedata
        label_eddypro_dyn_metadata = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_DYN_METADATA,
                                              font=self.BOLD_FONT).grid(sticky="w", row=i+33, column=0)
        info_eddypro_dyn_metadata = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                              command=self.on_click_eddypro_dyn_metadata).\
            grid(sticky="w", row=i+33, column=1)
        button_browse_eddypro_dyn_metadata = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_dyn_metadata).grid(sticky="w", row=i+33, column=2)
        desc_eddypro_dyn_matadata = tk.Label(second_frame, text=self.DESC_EDDYPRO_DYN_METADATA, font=self.DESC_FONT).\
            grid(sticky="w", row=i+34, column=0, columnspan=3)
        self.path_eddypro_dyn_metadata = tk.Label(master=second_frame, text=self.EDDYPRO_DYN_METADATA,
                                                  font=self.MAIN_FONT)
        self.path_eddypro_dyn_metadata.grid(sticky="w", row=i+35, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+36, column=0, columnspan=3)

        # create eddypro output path
        label_eddypro_output_path = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_OUTPUT_PATH,
                                             font=self.BOLD_FONT).grid(sticky="w", row=i+37, column=0)
        info_eddypro_output_path = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                             command=self.on_click_eddypro_output_path).\
            grid(sticky="w", row=i+37, column=1)
        button_browse_eddypro_output_path = tk.Button(master=second_frame, text="Browse",
                                                      font=self.MAIN_FONT, command=self.browse_eddypro_output_path). \
            grid(sticky="w", row=i+37, column=2)
        desc_eddypro_output_path = tk.Label(second_frame, text=self.DESC_EDDYPRO_OUTPUT_PATH, font=self.DESC_FONT).\
            grid(sticky="w", row=i+38, column=0, columnspan=3)
        self.path_eddypro_output_path = tk.Label(master=second_frame, text=self.EDDYPRO_OUTPUT_PATH,
                                                 font=self.MAIN_FONT)
        self.path_eddypro_output_path.grid(sticky="w", row=i+39, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+40, column=0, columnspan=3)

        # create eddypro input ghg path
        label_eddypro_input_ghg_path = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_INPUT_GHG_PATH,
                                                font=self.BOLD_FONT).grid(sticky="w", row=i+41, column=0)
        info_eddypro_input_ghg_path = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                command=self.on_click_eddypro_input_ghg_path).\
            grid(sticky="w", row=i+41, column=1)
        button_browse_eddypro_input_ghg_path = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_input_ghg_path).grid(sticky="w", row=i+41, column=2)
        desc_eddypro_input_ghg_path = tk.Label(second_frame, text=self.DESC_EDDYPRO_INPUT_GHG_PATH,
                                               font=self.DESC_FONT).grid(sticky="w", row=i+42, column=0, columnspan=3)
        self.path_eddypro_input_ghg_path = tk.Label(master=second_frame, text=self.EDDYPRO_INPUT_GHG_PATH,
                                                    font=self.MAIN_FONT)
        self.path_eddypro_input_ghg_path.grid(sticky="w", row=i+43, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+44, column=0, columnspan=3)

        #############################################################
        # create pyflux pro main title
        i = self.LINE_PYFLUX_PRO
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_pyfluxpro = tk.Label(master=second_frame, text=self.PYFLUXPROPRO_RUNNING_VARIABLE,
                                   font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+2, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+3, column=0, columnspan=3)

        # create pyfluxpro full output
        label_pyfluxpro_full_output = tk.Label(master=second_frame, text=self.BROWSE_FULL_OUTPUT_PYFLUXPRO,
                                               font=self.BOLD_FONT).grid(sticky="w", row=i+4, column=0)
        info_pyfluxpro_full_output = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                               command=self.on_click_pyfluxpro_full_output).\
            grid(sticky="w", row=i+4, column=1)
        button_browse_pyfluxpro_full_output = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_full_output).grid(sticky="w", row=i+4, column=2)
        desc_pyflux_pro_full_output = tk.Label(second_frame, text=self.DESC_FULL_OUTPUT_PYFLUXPRO, font=self.DESC_FONT)\
            .grid(sticky="w", row=i+5, column=0, columnspan=3)
        self.path_pyfluxpro_full_output = tk.Label(master=second_frame, text=self.FULL_OUTPUT_PYFLUXPRO,
                                                   font=self.MAIN_FONT)
        self.path_pyfluxpro_full_output.grid(sticky="w", row=i+6, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)

        # create pyfluxpro met data 30
        label_pyfluxpro_met_data = tk.Label(master=second_frame, text=self.BROWSE_MET_DATA_30_PYFLUXPRO,
                                            font=self.BOLD_FONT).grid(sticky="w", row=i+8, column=0)
        info_pyfluxpro_met_data = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                            command=self.on_click_pyfluxpro_met_data).\
            grid(sticky="w", row=i+8, column=1)
        button_browse_pyfluxpro_met_data = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_met_data).grid(sticky="w", row=i+8, column=2)
        desc_pyfluxpro_met_data = tk.Label(second_frame, text=self.DESC_MET_DATA_30_PYFLUXPRO, font=self.DESC_FONT).\
            grid(sticky="w", row=i+9, column=0, columnspan=3)
        self.path_pyfluxpro_met_data = tk.Label(master=second_frame, text=self.MET_DATA_30_PYFLUXPRO,
                                                font=self.MAIN_FONT)
        self.path_pyfluxpro_met_data.grid(sticky="w", row=i+10, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)

        # create pyfluxpro input sheet"
        label_pyfluxpro_input_sheet = tk.Label(master=second_frame, text=self.BROWSE_PYFLUXPRO_INPUT_SHEET,
                                               font=self.BOLD_FONT).grid(sticky="w", row=i+12, column=0)
        info_pyfluxpro_input_sheet = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                               command=self.on_click_pyfluxpro_input_sheet).\
            grid(sticky="w", row=i+12, column=1)
        button_browse_pyfluxpro_input_sheet = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_input_sheet).grid(sticky="w", row=i+12, column=2)
        desc_pyfluxpro_input_sheet = tk.Label(second_frame, text=self.DESC_PYFLUXPRO_INPUT_SHEET, font=self.DESC_FONT).\
            grid(sticky="w", row=i+13, column=0, columnspan=3)
        self.path_pyfluxpro_input_sheet = tk.Label(master=second_frame, text=self.PYFLUXPRO_INPUT_SHEET,
                                                   font=self.MAIN_FONT)
        self.path_pyfluxpro_input_sheet.grid(sticky="w", row=i+14, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+15, column=0, columnspan=3)

        # create pyfluxpro input ameriflux"
        label_pyfluxpro_input_ameriflux = tk.Label(master=second_frame, text=self.BROWSE_PYFLUXPRO_INPUT_AMERIFLUX,
                                                   font=self.BOLD_FONT).grid(sticky="w", row=i+16, column=0)
        info_pyfluxpro_input_ameriflux = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                   command=self.on_click_pyfluxpro_input_ameriflux). \
            grid(sticky="w", row=i+16, column=1)
        button_browse_pyfluxpro_input_ameriflux = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_input_ameriflux).grid(sticky="w", row=i+16, column=2)
        desc_pyfluxpro_input_ameriflux = tk.Label(second_frame, text=self.DESC_PYFLUXPRO_INPUT_AMERIFLUX,
                                                  font=self.DESC_FONT).\
            grid(sticky="w", row=i+17, column=0, columnspan=3)
        self.path_pyfluxpro_input_ameriflux = tk.Label(master=second_frame, text=self.PYFLUXPRO_INPUT_AMERIFLUX,
                                                       font=self.MAIN_FONT)
        self.path_pyfluxpro_input_ameriflux.grid(sticky="w", row=i+18, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+19, column=0, columnspan=3)

        #############################################################
        # create pyfluxpro ameriflux formatting main title
        i = self.LINE_PYFLUX_L1
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_pyfluxpro_l1 = tk.Label(master=second_frame, text=self.PYFLUXPROPRO_L1_VARIABLE,
                                      font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+2, column=0, columnspan=3)

        # creating user confirmation on erroring variables
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+3, columnspan=3)
        browse_ameriflux_variable_user_confirmation = tk.Label(
            second_frame, text=self.BROWSE_AMERIFLUX_VARIABLE_USER_CONFIRMATION, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+4, column=0)
        button_ameriflux_variable_user_confirmation = tk.Button(
            second_frame, text=self.INFO_TITLE, command=self.on_click_ameriflux_variable_user_confirmation). \
            grid(sticky="w", row=i+4, column=1)
        desc_ameriflux_variable_user_confirmation = tk.Label(
            second_frame, text=self.DESC_AMERIFLUX_VARIABLE_USER_CONFIRMATION, font=self.DESC_FONT). \
            grid(sticky="w", row=i+5, columnspan=3)
        confirm_ameriflux_variable_user_confirmation_list = ("Y", "N", "A")
        confirm_ameriflux_variables_user_confirmation_index = 0
        for index, value in enumerate(confirm_ameriflux_variable_user_confirmation_list):
            if value == self.AMERIFLUX_VARIABLE_USER_CONFIRMATION:
                confirm_ameriflux_variables_user_confirmation_index = index
        # n = tk.StringVar()
        self.combo_ameriflux_variable_confirm = ttk.Combobox(second_frame)
        self.combo_ameriflux_variable_confirm['values'] = confirm_ameriflux_variable_user_confirmation_list
        self.combo_ameriflux_variable_confirm.current(confirm_ameriflux_variables_user_confirmation_index)
        self.combo_ameriflux_variable_confirm.grid(sticky="w", row=i + 6, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)

        # create L1 mainstem input
        label_l1_mainstem_input = tk.Label(master=second_frame, text=self.BROWSE_L1_MAINSTEM_INPUT,
                                           font=self.BOLD_FONT).grid(sticky="w", row=i+8, column=0)
        info_l1_mainstem_input = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                           command=self.on_click_l1_mainstem_input).grid(sticky="w", row=i+8, column=1)
        button_browse_l1_mainstem_input = tk.Button(
            master=second_frame, text="Browse", font=self.MAIN_FONT, command=self.browse_l1_mainstem_input).\
            grid(sticky="w", row=i+8, column=2)
        desc_l1_mainstem_input = tk.Label(second_frame, text=self.DESC_L1_MAINSTEM_INPUT, font=self.DESC_FONT) \
            .grid(sticky="w", row=i+9, column=0, columnspan=3)
        self.path_l1_mainstem_input = tk.Label(master=second_frame, text=self.L1_MAINSTEM_INPUT, font=self.MAIN_FONT)
        self.path_l1_mainstem_input .grid(sticky="w", row=i+10, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)

        # create l1 ameriflux only input
        label_l1_ameriflux_only_input = tk.Label(master=second_frame, text=self.BROWSE_L1_AMERIFLUX_ONLY_INPUT,
                                                 font=self.BOLD_FONT).grid(sticky="w", row=i+12, column=0)
        info_l1_ameriflux_only_input = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                 command=self.on_click_l1_ameriflux_only_input). \
            grid(sticky="w", row=i+12, column=1)
        button_browse_l1_ameriflux_only_input = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l1_ameriflux_only_input).grid(sticky="w", row=i+12, column=2)
        desc_l1_ameriflux_only_input = tk.Label(
            second_frame, text=self.DESC_L1_AMERIFLUX_ONLY_INPUT, font=self.DESC_FONT). \
            grid(sticky="w", row=i+13, column=0, columnspan=3)
        self.path_l1_ameriflux_only_input = tk.Label(
            master=second_frame, text=self.L1_AMERIFLUX_ONLY_INPUT, font=self.MAIN_FONT)
        self.path_l1_ameriflux_only_input.grid(sticky="w", row=i+14, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+15, column=0, columnspan=3)

        # create L1 ameriflux mainstem key
        label_l1_mainstem_key = tk.Label(master=second_frame, text=self.BROWSE_L1_AMERIFLUX_MAINSTEM_KEY,
                                         font=self.BOLD_FONT).grid(sticky="w", row=i+16, column=0)
        info_l1_mainstem_key = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                         command=self.on_click_l1_mainstem_key). \
            grid(sticky="w", row=i+16, column=1)
        button_browse_l1_mainstem_key = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l1_mainstem_key).grid(sticky="w", row=i+16, column=2)
        desc_l1_mainstem_key = tk.Label(second_frame, text=self.DESC_L1_AMERIFLUX_MAINSTEM_KEY, font=self.DESC_FONT). \
            grid(sticky="w", row=i+17, column=0, columnspan=3)
        self.path_l1_mainstem_key = tk.Label(master=second_frame, text=self.L1_AMERIFLUX_MAINSTEM_KEY,
                                             font=self.MAIN_FONT)
        self.path_l1_mainstem_key.grid(sticky="w", row=i+18, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+19, column=0, columnspan=3)

        # create l1 ameriflux run output
        label_l1_ameriflux_run_output = tk.Label(master=second_frame, text=self.BROWSE_L1_AMERIFLUX_RUN_OUTPUT,
                                                 font=self.BOLD_FONT).grid(sticky="w", row=i+20, column=0)
        info_l1_ameriflux_run_output = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                 command=self.on_click_l1_ameriflux_run_output). \
            grid(sticky="w", row=i+20, column=1)
        button_browse_l1_ameriflux_run_output = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l1_ameriflux_run_output).grid(sticky="w", row=i+20, column=2)
        desc_l1_ameriflux_run_output = tk.Label(
            second_frame, text=self.DESC_L1_AMERIFLUX_RUN_OUTPUT, font=self.DESC_FONT). \
            grid(sticky="w", row=i+21, column=0, columnspan=3)
        self.path_l1_ameriflux_run_output = tk.Label(
            master=second_frame, text=self.L1_AMERIFLUX_RUN_OUTPUT, font=self.MAIN_FONT)
        self.path_l1_ameriflux_run_output.grid(sticky="w", row=i+22, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+23, column=0, columnspan=3)

        # create L1 output ameriflux"
        label_l1_ameriflux = tk.Label(master=second_frame, text=self.BROWSE_L1_AMERIFLUX,
                                      font=self.BOLD_FONT).grid(sticky="w", row=i+24, column=0)
        info_l1_ameriflux = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                      command=self.on_click_l1_ameriflux). \
            grid(sticky="w", row=i+24, column=1)
        button_browse_l1_ameriflux = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l1_ameriflux).grid(sticky="w", row=i+24, column=2)
        desc_l1_ameriflux = tk.Label(second_frame, text=self.DESC_L1_AMERIFLUX, font=self.DESC_FONT). \
            grid(sticky="w", row=i+25, column=0, columnspan=3)
        self.path_l1_ameriflux = tk.Label(master=second_frame, text=self.L1_AMERIFLUX, font=self.MAIN_FONT)
        self.path_l1_ameriflux.grid(sticky="w", row=i+26, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+27, column=0, columnspan=3)

        # create L1 ameriflux erroring variables
        label_l1_ameriflux_erroring_variables_key = tk.Label(
            master=second_frame, text=self.BROWSE_L1_AMERIFLUX_ERRORING_VARIABLES_KEY, font=self.BOLD_FONT).\
            grid(sticky="w", row=i+28, column=0)
        info_l1_ameriflux_erroring_variables_key = tk.Button(
            second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
            command=self.on_click_l1_ameriflux_erroring_variables_key). \
            grid(sticky="w", row=i+28, column=1)
        button_browse_l1_ameriflux_erroring_variables_key = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l1_ameriflux_erroring_variables_key).grid(sticky="w", row=i+28, column=2)
        desc_l1_ameriflux_erroring_variables_key = tk.Label(
            second_frame, text=self.DESC_L1_AMERIFLUX_ERRORING_VARIABLES_KEY, font=self.DESC_FONT). \
            grid(sticky="w", row=i+29, column=0, columnspan=3)
        self.path_l1_ameriflux_erroring_variables_key = tk.Label(
            master=second_frame, text=self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY, font=self.MAIN_FONT)
        self.path_l1_ameriflux_erroring_variables_key.grid(sticky="w", row=i+30, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB).\
            grid(sticky="w", row=i+31, column=0, columnspan=3)

        # create L2 mainstem input
        label_l2_mainstem_input = tk.Label(master=second_frame, text=self.BROWSE_L2_MAINSTEM_INPUT,
                                           font=self.BOLD_FONT).grid(sticky="w", row=i+32, column=0)
        info_l2_mainstem_input = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                           command=self.on_click_l2_mainstem_input). \
            grid(sticky="w", row=i+32, column=1)
        button_browse_l2_mainstem_input = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l2_mainstem_input).grid(sticky="w", row=i+32, column=2)
        desc_l2_mainstem_input = tk.Label(second_frame, text=self.DESC_L2_MAINSTEM_INPUT, font=self.DESC_FONT). \
            grid(sticky="w", row=i+33, column=0, columnspan=3)
        self.path_l2_mainstem_input = tk.Label(master=second_frame, text=self.L2_MAINSTEM_INPUT, font=self.MAIN_FONT)
        self.path_l2_mainstem_input.grid(sticky="w", row=i+34, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+35, column=0, columnspan=3)

        # create l2 ameriflux only input
        label_l2_ameriflux_only_input = tk.Label(master=second_frame, text=self.BROWSE_L2_AMERIFLUX_ONLY_INPUT,
                                                 font=self.BOLD_FONT).grid(sticky="w", row=i+36, column=0)
        info_l2_ameriflux_only_input = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                 command=self.on_click_l2_ameriflux_only_input). \
            grid(sticky="w", row=i+36, column=1)
        button_browse_l2_ameriflux_only_input = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l2_ameriflux_only_input).grid(sticky="w", row=i+36, column=2)
        desc_l2_ameriflux_only_input = tk.Label(
            second_frame, text=self.DESC_L2_AMERIFLUX_ONLY_INPUT, font=self.DESC_FONT). \
            grid(sticky="w", row=i+37, column=0, columnspan=3)
        self.path_l2_ameriflux_only_input = tk.Label(
            master=second_frame, text=self.L2_AMERIFLUX_ONLY_INPUT, font=self.MAIN_FONT)
        self.path_l2_ameriflux_only_input.grid(sticky="w", row=i+37, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+38, column=0, columnspan=3)

        # create l2 ameriflux run output
        label_l2_ameriflux_run_output = tk.Label(master=second_frame, text=self.BROWSE_L2_AMERIFLUX_RUN_OUTPUT,
                                                 font=self.BOLD_FONT).grid(sticky="w", row=i+40, column=0)
        info_l2_ameriflux_run_output = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                                 command=self.on_click_l2_ameriflux_run_output). \
            grid(sticky="w", row=i+40, column=1)
        button_browse_l2_ameriflux_run_output = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l2_ameriflux_run_output).grid(sticky="w", row=i+40, column=2)
        desc_l2_ameriflux_run_output = tk.Label(
            second_frame, text=self.DESC_L2_AMERIFLUX_RUN_OUTPUT, font=self.DESC_FONT). \
            grid(sticky="w", row=i+41, column=0, columnspan=3)
        self.path_l2_ameriflux_run_output = tk.Label(
            master=second_frame, text=self.L2_AMERIFLUX_RUN_OUTPUT, font=self.MAIN_FONT)
        self.path_l2_ameriflux_run_output.grid(sticky="w", row=i+42, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+43, column=0, columnspan=3)

        # create L2 output ameriflux"
        label_l2_ameriflux = tk.Label(master=second_frame, text=self.BROWSE_L2_AMERIFLUX,
                                      font=self.BOLD_FONT).grid(sticky="w", row=i+44, column=0)
        info_l2_ameriflux = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                      command=self.on_click_l2_ameriflux). \
            grid(sticky="w", row=i+44, column=1)
        button_browse_l2_ameriflux = \
            tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_l2_ameriflux).grid(sticky="w", row=i+44, column=2)
        desc_l2_ameriflux = tk.Label(second_frame, text=self.DESC_L2_AMERIFLUX, font=self.DESC_FONT). \
            grid(sticky="w", row=i+45, column=0, columnspan=3)
        self.path_l2_ameriflux = tk.Label(master=second_frame, text=self.L2_AMERIFLUX, font=self.MAIN_FONT)
        self.path_l2_ameriflux.grid(sticky="w", row=i+46, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+47, column=0, columnspan=3)

        #############################################################
        # create save frame
        i = self.LINE_SAVE_ENV
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_eddypro_save = tk.Label(master=second_frame, text=self.SAVE_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        button_save_env = tk.Button(master=second_frame, width=25, text=self.SAVE_ENV_FILE, font=self.MAIN_FONT,
                                    command=self.save_env).grid(sticky="w", row=i+3, column=0, columnspan=3)

        root.mainloop()

    def browse_sftp_ghg_local_path(self):
        filepath = self.SFTP_GHG_LOCAL_PATH
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)

        if filepath != "":
            self.path_sftp_ghg_local_path.config(text=filepath)
            self.SFTP_GHG_LOCAL_PATH = filepath

    def browse_sftp_met_local_path(self):
        filepath = self.SFTP_MET_LOCAL_PATH
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            self.path_sftp_met_local_path.config(text=filepath)
            self.SFTP_MET_LOCAL_PATH = filepath

    def browse_input_met(self):
        filepath = self.INPUT_MET
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("csv files", "*.csv")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".csv")
            self.path_input_met.config(text=filepath)
            self.INPUT_MET = filepath

    def browse_input_precip(self):
        filepath = self.INPUT_PRECIP
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".xlsx")
            self.path_input_precip.config(text=filepath)
            self.INPUT_PRECIP = filepath

    def browse_master_met(self):
        filepath = self.MASTER_MET
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            filepath = os.path.join(filepath, 'met_output.csv')
            self.path_master_met.config(text=filepath)
            self.MASTER_MET = filepath

    def browse_input_soil_key(self):
        filepath = self.INPUT_SOIL_KEY
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".xlsx")
            self.path_input_soil_key.config(text=filepath)
            self.INPUT_SOIL_KEY = filepath

    def browse_eddypro_bin(self):
        filepath = self.EDDYPRO_BIN_LOC
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            self.path_eddypro_bin.config(text=filepath)
            self.EDDYPRO_BIN_LOC = filepath

    def browse_eddypro_proj_template(self):
        filepath = self.EDDYPRO_PROJ_FILE_TEMPLATE
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".eddypro")
            self.path_eddypro_proj_template.config(text=filepath)
            self.EDDYPRO_PROJ_FILE_TEMPLATE = filepath

    def browse_eddypro_proj_file_name(self):
        filepath = self.EDDYPRO_PROJ_FILE_NAME
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".eddypro")
            self.path_eddypro_proj_file_name.config(text=filepath)
            self.EDDYPRO_PROJ_FILE_NAME = filepath

    def browse_eddypro_proj_file(self):
        filepath = self.EDDYPRO_PROJ_FILE
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("metadata files", "*.metadata")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".metadata")
            self.path_eddypro_proj_file.config(text=filepath)
            self.EDDYPRO_PROJ_FILE = filepath

    def browse_eddypro_dyn_metadata(self):
        filepath = self.EDDYPRO_DYN_METADATA
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("csv files", "*.csv")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".csv")
            self.path_eddypro_dyn_metadata.config(text=filepath)
            self.EDDYPRO_DYN_METADATA = filepath

    def browse_eddypro_output_path(self):
        filepath = self.EDDYPRO_OUTPUT_PATH
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            self.path_eddypro_output_path.config(text=filepath)
            self.EDDYPRO_OUTPUT_PATH = filepath

    def browse_eddypro_input_ghg_path(self):
        filepath = self.EDDYPRO_INPUT_GHG_PATH
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            self.path_eddypro_input_ghg_path.config(text=filepath)
            self.EDDYPRO_INPUT_GHG_PATH = filepath

    def browse_pyfluxpro_full_output(self):
        filepath = self.FULL_OUTPUT_PYFLUXPRO
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            filepath = os.path.join(filepath, "full_output.csv")
            self.path_pyfluxpro_full_output.config(text=filepath)
            self.FULL_OUTPUT_PYFLUXPRO = filepath

    def browse_pyfluxpro_met_data(self):
        filepath = self.MET_DATA_30_PYFLUXPRO
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askdirectory(initialdir=initialdir)
        if filepath != "":
            filepath = os.path.join(filepath, "Met_data_30.csv")
            self.path_pyfluxpro_met_data.config(text=filepath)
            self.MET_DATA_30_PYFLUXPRO = filepath

    def browse_pyfluxpro_input_sheet(self):
        filepath = self.PYFLUXPRO_INPUT_SHEET
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".xlsx")
            self.path_pyfluxpro_input_sheet.config(text=filepath)
            self.PYFLUXPRO_INPUT_SHEET = filepath

    def browse_pyfluxpro_input_ameriflux(self):
        filepath = self.PYFLUXPRO_INPUT_AMERIFLUX
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_pyfluxpro_input_ameriflux.config(text=filepath)
            self.PYFLUXPRO_INPUT_AMERIFLUX = filepath

    def browse_l1_mainstem_input(self):
        filepath = self.L1_MAINSTEM_INPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l1_mainstem_input.config(text=filepath)
            self.L1_MAINSTEM_INPUT = filepath

    def browse_l1_ameriflux_only_input(self):
        filepath = self.L1_AMERIFLUX_ONLY_INPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l1_ameriflux_only_input.config(text=filepath)
            self.L1_AMERIFLUX_ONLY_INPUT = filepath

    def browse_l1_mainstem_key(self):
        filepath = self.L1_AMERIFLUX_MAINSTEM_KEY
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".xlsx")
            self.path_l1_mainstem_key.config(text=filepath)
            self.L1_AMERIFLUX_MAINSTEM_KEY = filepath

    def browse_l1_ameriflux_run_output(self):
        filepath = self.L1_AMERIFLUX_RUN_OUTPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("nc files", "*.nc")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".nc")
            self.path_l1_ameriflux_run_output.config(text=filepath)
            self.L1_AMERIFLUX_RUN_OUTPUT = filepath

    def browse_l1_ameriflux(self):
        filepath = self.L1_AMERIFLUX
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l1_ameriflux.config(text=filepath)
            self.L1_AMERIFLUX = filepath

    def browse_l1_ameriflux_erroring_variables_key(self):
        filepath = self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".xlsx")
            self.path_l1_ameriflux_erroring_variables_key.config(text=filepath)
            self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY = filepath

    def browse_l2_mainstem_input(self):
        filepath = self.L2_MAINSTEM_INPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])

        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l2_mainstem_input.config(text=filepath)
            self.L2_MAINSTEM_INPUT = filepath

    def browse_l2_ameriflux_only_input(self):
        filepath = self.L2_AMERIFLUX_ONLY_INPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])

        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l2_ameriflux_only_input.config(text=filepath)
            self.L2_AMERIFLUX_ONLY_INPUT = filepath

    def browse_l2_ameriflux_run_output(self):
        filepath = self.L2_AMERIFLUX_RUN_OUTPUT
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("nc files", "*.nc")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".nc")
            self.path_l2_ameriflux_run_output.config(text=filepath)
            self.L2_AMERIFLUX_RUN_OUTPUT = filepath

    def browse_l2_ameriflux(self):
        filepath = self.L2_AMERIFLUX
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("txt files", "*.txt")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".txt")
            self.path_l2_ameriflux.config(text=filepath)
            self.L2_AMERIFLUX = filepath

    def check_extension_and_add(self, instring, extension):
        # parset the extension
        filename, file_extension = os.path.splitext(instring)
        if file_extension.lower() != extension.lower():
            # add given extension to the end of the string
            instring = instring + extension

        return instring

    def preset_variables(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.SFTP_CONFIRMATION = "N"
        self.SFTP_SERVER = "remote.ftp.server.url"
        self.SFTP_USERNAME = "username"
        self.SFTP_PASSWORD = "password"
        self.SFTP_GHG_REMOTE_PATH = "remote/path/for/ghg/file/folder"
        self.SFTP_GHG_LOCAL_PATH = current_dir + "/data/eddypro/input"
        self.SFTP_MET_REMOTE_PATH = "remote/path/for/met/data"
        self.SFTP_MET_LOCAL_PATH = current_dir + "/data/master_met/input"

        self.MISSING_TIME_USER_CONFIRMATION = "Y"

        self.INPUT_MET = current_dir + "/data/master_met/input"
        self.INPUT_PRECIP = current_dir + "/data/master_met/input"
        self.MISSING_TIME = "96"
        self.MASTER_MET = current_dir + "/data/master_met/output"
        self.INPUT_SOIL_KEY = current_dir + "/data/eddypro/input"

        if self.OS_PLATFORM.lower() == "windows":
            self.EDDYPRO_BIN_LOC = "C:/Program Files/LI-COR/EddyPro-7.0.7/bin"
        elif self.OS_PLATFORM.lower() == "os x":
            self.EDDYPRO_BIN_LOC = "/Applications/eddypro.app/Contents/MacOS/bin"
        else:
            raise Exception("The current platform is currently not being supported.")

        self.EDDYPRO_PROJ_FILE_TEMPLATE = current_dir + "/data/templates"
        self.EDDYPRO_PROJ_FILE_NAME = current_dir + "/data/templates"
        self.EDDYPRO_PROJ_TITLE = "Project Title"
        self.EDDYPRO_PROJ_ID = "Project ID"
        self.EDDYPRO_FILE_PROTOTYPE = "yyyy-mm-ddTHHMM??_Sorghum-00137.ghg"
        self.EDDYPRO_PROJ_FILE = current_dir + "/data/eddypro/input"
        self.EDDYPRO_DYN_METADATA = current_dir + "data/eddypro/input"
        self.EDDYPRO_OUTPUT_PATH = current_dir + "/data/eddypro/output"
        self.EDDYPRO_INPUT_GHG_PATH = current_dir + "/data/eddypro/input"

        self.FULL_OUTPUT_PYFLUXPRO = current_dir + "/data/pyfluxpro/output"
        self.MET_DATA_30_PYFLUXPRO = current_dir + "/data/pyfluxpro/output"
        self.PYFLUXPRO_INPUT_SHEET = current_dir + "/data/pyfluxpro/output"
        self.PYFLUXPRO_INPUT_AMERIFLUX = current_dir + "/data/pyfluxpro/output"

        self.AMERIFLUX_VARIABLE_USER_CONFIRMATION = "N"
        self.L1_MAINSTEM_INPUT = current_dir + "/data/pyfluxpro/input"
        self.L1_AMERIFLUX_ONLY_INPUT = current_dir + "/data/pyfluxpro/input_ameriflux"
        self.L1_AMERIFLUX_MAINSTEM_KEY = current_dir + "/data/pyfluxpro/input_ameriflux"
        self.L1_AMERIFLUX_RUN_OUTPUT = current_dir + "/data/pyfluxpro/output_ameriflux"
        self.L1_AMERIFLUX = current_dir + "/data/pyfluxpro/output_ameriflux"
        self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY = current_dir + "/data/pyfluxpro/input_ameriflux"
        self.L2_MAINSTEM_INPUT = current_dir + "/data/pyfluxpro/input"
        self.L2_AMERIFLUX_ONLY_INPUT = current_dir + "/data/pyfluxpro/input_ameriflux"
        self.L2_AMERIFLUX_RUN_OUTPUT = current_dir + "/data/pyfluxpro/output_ameriflux"
        self.L2_AMERIFLUX = current_dir + "/data/pyfluxpro/output_ameriflux"

    def save_env(self):
        sftp_title_line = "# Sync files from the server"
        sftp_confirm_line = "SFTP_CONFIRMATION=" + self.combo_sftp_confirm.get()
        sftp_server_line = "SFTP_SERVER=" + str(self.sftp_server.get())
        sftp_username_line = "SFTP_USERNAME=" + str(self.sftp_username.get())
        sftp_password_line = "SFTP_PASSWORD=" + str(self.sftp_password.get())
        sftp_ghg_remote_path_line = "SFTP_GHG_REMOTE_PATH=" + str(self.sftp_ghg_remote_path.get())
        sftp_ghg_local_path_line = "SFTP_GHG_LOCAL_PATH=" + self.SFTP_GHG_LOCAL_PATH
        sftp_met_remote_path_line = "SFTP_MET_REMOTE_PATH=" + str(self.sftp_met_remote_path.get())
        sftp_met_local_path_line = "SFTP_MET_LOCAL_PATH=" + self.SFTP_MET_LOCAL_PATH

        eddypro_input_title_line = "# Variables for EddyPro formatting"
        user_conform_line = "MISSING_TIME_USER_CONFIRMATION=" + self.combo_confirm.get()
        eddypro_input_met_line = "INPUT_MET=" + self.INPUT_MET
        eddypro_input_precip_line = "INPUT_PRECIP=" + self.INPUT_PRECIP
        eddypro_missing_time_line = "MISSING_TIME=" + str(self.missing_time.get())
        eddypro_master_met_line = "MASTER_MET=" + self.MASTER_MET
        eddypro_input_soil_key_line = "INPUT_SOIL_KEY=" + self.INPUT_SOIL_KEY

        eddypro_run_title_line = "# Variables for EddyPro running"
        eddypro_bin_loc_line = "EDDYPRO_BIN_LOC=" + self.EDDYPRO_BIN_LOC
        eddypro_proj_template_line = "EDDYPRO_PROJ_FILE_TEMPLATE=" + self.EDDYPRO_PROJ_FILE_TEMPLATE
        eddypro_proj_file_name_line = "EDDYPRO_PROJ_FILE_NAME=" + self.EDDYPRO_PROJ_FILE_NAME
        eddypro_proj_title_line = "EDDYPRO_PROJ_TITLE=" + self.eddypro_proj_title.get()
        eddypro_proj_id_line = "EDDYPRO_PROJ_ID=" + self.eddypro_proj_id.get()
        eddypro_file_prototype_line = "EDDYPRO_FILE_PROTOTYPE=" + self.eddypro_file_prototype.get()
        eddypro_proj_file_line = "EDDYPRO_PROJ_FILE=" + self.EDDYPRO_PROJ_FILE
        eddypro_dyn_metadata_line = "EDDYPRO_DYN_METADATA=" + self.EDDYPRO_DYN_METADATA
        eddypro_output_path_line = "EDDYPRO_OUTPUT_PATH=" + self.EDDYPRO_OUTPUT_PATH
        eddypro_input_ghg_path_line = "EDDYPRO_INPUT_GHG_PATH=" + self.EDDYPRO_INPUT_GHG_PATH

        pyfluxpro_title_line = "# Variables for PyFluxPro running"
        pyfluxpro_full_output_line = "FULL_OUTPUT_PYFLUXPRO=" + self.FULL_OUTPUT_PYFLUXPRO
        pyfluxpro_met_data_line = "MET_DATA_30_PYFLUXPRO=" + self.MET_DATA_30_PYFLUXPRO
        pyfluxpro_input_sheet_line = "PYFLUXPRO_INPUT_SHEET=" + self.PYFLUXPRO_INPUT_SHEET
        pyfluxpro_input_ameriflux_line = "PYFLUXPRO_INPUT_AMERIFLUX=" + self.PYFLUXPRO_INPUT_AMERIFLUX

        pyfluxpro_l1_line = "# Variables for PyFluxPro AmeriFlux formatting"
        pyfluxpro_l1_user_confirmation_line = "AMERIFLUX_VARIABLE_USER_CONFIRMATION=" + \
                                              self.combo_ameriflux_variable_confirm.get()
        pyfluxpro_l1_mainstem_input_line = "L1_MAINSTEM_INPUT=" + self.L1_MAINSTEM_INPUT
        pyfluxpro_l1_ameriflux_only_input_line = "L1_AMERIFLUX_ONLY_INPUT=" + self.L1_AMERIFLUX_ONLY_INPUT
        pyfluxpro_l1_ameriflux_mainstem_key_line = "L1_AMERIFLUX_MAINSTEM_KEY=" + self.L1_AMERIFLUX_MAINSTEM_KEY
        pyfluxpro_l1_ameriflux_run_output_line = "L1_AMERIFLUX_RUN_OUTPUT=" + self.L1_AMERIFLUX_RUN_OUTPUT
        pyfluxpro_l1_ameriflux_line = "L1_AMERIFLUX=" + self.L1_AMERIFLUX
        pyfluxpro_l1_error_variables_key_line = \
            "L1_AMERIFLUX_ERRORING_VARIABLES_KEY=" + self.L1_AMERIFLUX_ERRORING_VARIABLES_KEY
        pyfluxpro_l2_mainstem_input_line = "L2_MAINSTEM_INPUT=" + self.L2_MAINSTEM_INPUT
        pyfluxpro_l2_ameriflux_only_input_line = "L2_AMERIFLUX_ONLY_INPUT=" + self.L2_AMERIFLUX_ONLY_INPUT
        pyfluxpro_l2_ameriflux_run_output_line = "L2_AMERIFLUX_RUN_OUTPUT=" + self.L2_AMERIFLUX_RUN_OUTPUT
        pyfluxpro_l2_ameriflux_line = "L2_AMERIFLUX=" + self.L2_AMERIFLUX

        lines = [
            sftp_title_line, sftp_confirm_line, sftp_server_line, sftp_username_line,
            sftp_password_line, sftp_ghg_remote_path_line, sftp_ghg_local_path_line,
            sftp_met_remote_path_line, sftp_met_local_path_line,
            "",
            eddypro_input_title_line, user_conform_line, eddypro_input_met_line, eddypro_input_precip_line,
            eddypro_missing_time_line, eddypro_master_met_line, eddypro_input_soil_key_line,
            "",
            eddypro_run_title_line, eddypro_bin_loc_line, eddypro_proj_template_line, eddypro_proj_file_name_line,
            eddypro_proj_title_line, eddypro_proj_id_line, eddypro_file_prototype_line, eddypro_proj_file_line,
            eddypro_dyn_metadata_line, eddypro_output_path_line, eddypro_input_ghg_path_line,
            "",
            pyfluxpro_title_line, pyfluxpro_full_output_line, pyfluxpro_met_data_line, pyfluxpro_input_sheet_line,
            pyfluxpro_input_ameriflux_line,
            "",
            pyfluxpro_l1_line, pyfluxpro_l1_user_confirmation_line, pyfluxpro_l1_mainstem_input_line,
            pyfluxpro_l1_ameriflux_only_input_line, pyfluxpro_l1_ameriflux_mainstem_key_line,
            pyfluxpro_l1_ameriflux_run_output_line, pyfluxpro_l1_ameriflux_line, pyfluxpro_l1_error_variables_key_line,
            pyfluxpro_l2_mainstem_input_line, pyfluxpro_l2_ameriflux_only_input_line,
            pyfluxpro_l2_ameriflux_run_output_line, pyfluxpro_l2_ameriflux_line
        ]

        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

        answer = messagebox.askokcancel(title='Info', message="Would you like to save .env file?")
        if not answer:
            print(".env file not saved.")
        else:
            with open(outfile, 'w') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
                print(".env file saved.")

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_click_sftp_confirm(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_CONFIRMATION)

    def on_click_sftp_server(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_SERVER)

    def on_click_sftp_username(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_USERNAME)

    def on_click_sftp_password(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_PASSWORD)

    def on_click_sftp_ghg_remote_path(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_GHG_REMOTE_PATH)

    def on_click_sftp_ghg_local_path(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_GHG_LOCAL_PATH)

    def on_click_sftp_met_remote_path(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_MET_REMOTE_PATH)

    def on_click_sftp_met_local_path(self):
        tk.messagebox.showinfo("Info", self.INFO_SFTP_MET_LOCAL_PATH)

    def on_click_user_confirm(self):
        tk.messagebox.showinfo("Info", self.INFO_MISSING_TIME_USER_CONFIRMATION)

    def on_click_input_met(self):
        tk.messagebox.showinfo("Info", self.INFO_INPUT_MET)

    def on_click_input_precip(self):
        tk.messagebox.showinfo("Info", self.INFO_INPUT_PRECIP)

    def on_click_missing_time(self):
        tk.messagebox.showinfo("Info", self.INFO_MISSING_TIME)

    def on_click_master_met(self):
        tk.messagebox.showinfo("Info", self.INFO_MASTER_MET)

    def on_click_soil_key(self):
        tk.messagebox.showinfo("Info", self.INFO_INPUT_SOIL_KEY)

    def on_click_eddypro_bin(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_BIN)

    def on_click_eddypro_proj_template(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROJ_TEMPLATE)

    def on_click_eddypro_proj_file_name(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROJ_FILE_NAME)

    def on_click_eddypro_proj_title(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROJ_TITLE)

    def on_click_eddypro_proj_id(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROJ_ID)

    def on_click_eddypro_file_prototype(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_FILE_PROTOTYPE)

    def on_click_eddypro_proj_file(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROJ_FILE)

    def on_click_eddypro_dyn_metadata(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_DYN_METADATA)

    def on_click_eddypro_output_path(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_OUTPUT_PATH)

    def on_click_eddypro_input_ghg_path(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_INPUT_GHG_PATH)

    def on_click_pyfluxpro_full_output(self):
        tk.messagebox.showinfo("Info", self.INFO_FULL_OUTPUT_PYFLUXPRO)

    def on_click_pyfluxpro_met_data(self):
        tk.messagebox.showinfo("Info", self.INFO_MET_DATA_30_PYFLUXPRO)

    def on_click_pyfluxpro_input_sheet(self):
        tk.messagebox.showinfo("Info", self.INFO_PYFLUXPRO_INPUT_SHEET)

    def on_click_pyfluxpro_input_ameriflux(self):
        tk.messagebox.showinfo("Info", self.INFO_PYFLUXPRO_INPUT_AMERIFLUX)

    def on_click_ameriflux_variable_user_confirmation(self):
        tk.messagebox.showinfo("Info", self.INFO_AMERIFLUX_VARIABLE_USER_CONFIRMATION)

    def on_click_l1_mainstem_input(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_MAINSTEM_INPUT)

    def on_click_l1_ameriflux_only_input(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_AMERIFLUX_ONLY_INPUT)

    def on_click_l1_mainstem_key(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_AMERIFLUX_MAINSTEM_KEY)

    def on_click_l1_ameriflux_run_output(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_AMERIFLUX_RUN_OUTPUT)

    def on_click_l1_ameriflux(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_AMERIFLUX)

    def on_click_l1_ameriflux_erroring_variables_key(self):
        tk.messagebox.showinfo("Info", self.INFO_L1_AMERIFLUX_ERRORING_VARIABLES_KEY)

    def on_click_l2_mainstem_input(self):
        tk.messagebox.showinfo("Info", self.INFO_L2_MAINSTEM_INPUT)

    def on_click_l2_ameriflux_only_input(self):
        tk.messagebox.showinfo("Info", self.INFO_L2_AMERIFLUX_ONLY_INPUT)

    def on_click_l2_ameriflux_run_output(self):
        tk.messagebox.showinfo("Info", self.INFO_L2_AMERIFLUX_RUN_OUTPUT)

    def on_click_l2_ameriflux(self):
        tk.messagebox.showinfo("Info", self.INFO_L2_AMERIFLUX)


if __name__ == '__main__':
    app = EnvEditor()
