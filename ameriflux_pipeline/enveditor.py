# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made availabel under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is availabel at https://www.mozilla.org/en-US/MPL/2.0/

import os
import tkinter as tk

from tkinter import ttk as ttk
from tkinter import tix as tix
from tkinter import filedialog, messagebox
from dotenv import load_dotenv


class EnvEditor():
    def __init__(self):
        # text variables
        self.SEPARATION_LABEL = "---------------------------------------------------------"
        self.SEPARATION_LABEL_SUB = "------------------"
        self.INFO_TITLE = "info"

        self.LINE_USER_CONFIRMATION = 0
        self.LINE_EDDYPRO_FORMAT = 5
        self.LINE_EDDYPRO_RUN = 29
        self.LINE_PYFLUX_PRO = 74
        self.LINE_SAVE_ENV = 90

        self.USER_CONFIRMATION_LABEL = " User confirmation"
        self.BROWSE_USER_CONFIRAMTION = " Missing Timestamp Confirmation"
        self.DESC_USER_CONFIRMATION = " user decision on whether to insert, ignore or ask during runtime in case of " \
                                      "large number of missing timestamps"
        self.INFO_USER_CONFIRMATION = "When the pipeline encounters a data gap, would you like it to (1) Y - insert " \
                                      "empty time periods, (2) N - ignore the gap and return only time periods for " \
                                      "which there is data, or (3) A - stop running and ask you? For (3), you can " \
                                      "set the threshold for notification in \"Missing Time\". The choices will be " \
                                      "asked only if the number of missing timestamps are bigger than missing " \
                                      "timestamps thresholds"

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

        self.SAVE_LABEL = "Save .env file"
        self.SAVE_ENV_FILE = "Save"

        # font variables
        self.MAIN_BOLD_FONT = "Times 14 bold"
        self.MAIN_FONT = "Times 11"
        self.BOLD_FONT = "Times 11 bold"
        self.DESC_FONT = "Times 10 italic"

        # Load .env file
        load_dotenv()

        self.USER_CONFIRMATION = os.getenv('USER_CONFIRMATION')

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

        self.run()

    def run(self):
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
        i = self.LINE_USER_CONFIRMATION
        # create user confirmation
        label_user_confirm = tk.Label(second_frame, text=self.USER_CONFIRMATION_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i, columnspan=3)
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+1, columnspan=3)
        browse_user_confirm = tk.Label(second_frame, text=self.BROWSE_USER_CONFIRAMTION, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+2, column=0)
        button_uesr_confirm = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_user_confirm).\
            grid(sticky="w", row=i+2, column=1)
        desc_user_confirm = tk.Label(second_frame, text=self.DESC_USER_CONFIRMATION, font=self.DESC_FONT). \
            grid(sticky="w", row=i+3, columnspan=3)
        confirm_list = ("Y", "N", "A")
        confirm_list_index = 0
        for index, value in enumerate(confirm_list):
            if value == self.USER_CONFIRMATION:
                confirm_list_index = index
        n = tk.StringVar()
        self.combo_confirm = ttk.Combobox(second_frame)
        self.combo_confirm['values'] = confirm_list
        self.combo_confirm.current(confirm_list_index)
        self.combo_confirm.grid(sticky="w", row=i+4, columnspan=3)

        #############################################################
        i = self.LINE_EDDYPRO_FORMAT
        # create eddypro format main label
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, columnspan=3)
        label_eddypro_format = tk.Label(master=second_frame, text=self.EDDYPRO_FORMAT_VARIABLE,
                                        font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+2, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL).\
            grid(sticky="w", row=i+3, columnspan=3)

        # create eddypro format input meteorology data
        label_input_met = tk.Label(master=second_frame, text=self.BROWSE_INPUT_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+4, column=0)
        button_info_input_met = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_input_met). \
            grid(sticky="w", row=i+4, column=1)
        button_browse_input_met = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                            command=self.browse_input_met). \
            grid(sticky="w", row=i+4, column=2)
        desc_input_met = tk.Label(second_frame, text=self.DESC_INPUT_MET, font=self.DESC_FONT).\
            grid(sticky="w", row=i+5, column=0, columnspan=3)
        self.path_input_met = tk.Label(master=second_frame, text=self.INPUT_MET, font=self.MAIN_FONT)
        self.path_input_met.grid(sticky="w", row=i+6, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)

        # create eddypro format input precipitation data
        label_input_precip = tk.Label(master=second_frame, text=self.BROWSE_INPUT_PRECIP, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+8, column=0)
        button_info_input_precip = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_input_precip). \
            grid(sticky="w", row=i+8, column=1)
        button_browse_input_precip = tk.Button(master=second_frame, text="Browse", font=self.MAIN_FONT,
                                               command=self.browse_input_precip). \
            grid(sticky="w", row=i+8, column=2)
        desc_input_precip = tk.Label(second_frame, text=self.DESC_INPUT_PRECIP, font=self.DESC_FONT).\
            grid(sticky="w", row=i+9, column=0, columnspan=3)
        self.path_input_precip = tk.Label(master=second_frame, text=self.INPUT_PRECIP, font=self.MAIN_FONT)
        self.path_input_precip.grid(sticky="w", row=i+10, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+11, column=0, columnspan=3)

        # create eddypro format missing time
        missing_time_label = tk.Label(master=second_frame, text="Missing Time", font=self.BOLD_FONT). \
            grid(sticky="w", row=i+12, column=0)
        button_info_missing_time = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_missing_time).\
            grid(sticky="w", row=i+12, column=1, columnspan=2)
        desc_missing_time = tk.Label(second_frame, text=self.DESC_MISSING_TIME, font=self.DESC_FONT).\
            grid(sticky="w", row=i+13, column=0, columnspan=3)
        self.missing_time = tk.Entry(master=second_frame, width=10, font=self.MAIN_FONT)
        if self.MISSING_TIME is not None:
            self.missing_time.insert(0, self.MISSING_TIME)
        self.missing_time.grid(sticky="w", row=i+14, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+15, column=0, columnspan=3)

        # create eddypro format master met
        label_master_met = tk.Label(master=second_frame, text=self.BROWSE_MASTER_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+16, column=0)
        button_info_master_met = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_master_met).\
            grid(sticky="w", row=i+16, column=1)
        button_browse_input_master_met = tk.Button(master=second_frame, text="Browse",
                                                   font=self.MAIN_FONT, command=self.browse_master_met). \
            grid(sticky="w", row=i+16, column=2)
        desc_master_met = tk.Label(second_frame, text=self.DESC_MASTER_MET, font=self.DESC_FONT).\
            grid(sticky="w", row=i+17, column=0, columnspan=2)
        self.path_master_met = tk.Label(master=second_frame, text=self.MASTER_MET, font=self.MAIN_FONT)
        self.path_master_met.grid(sticky="w", row=i+18, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+19, column=0, columnspan=3)

        # create eddypro format input soil key
        label_soil_key = tk.Label(master=second_frame, text=self.BROWSE_INPUT_SOIL_KEY, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+20, column=0)
        button_info_soil_key = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_soil_key).\
            grid(sticky="w", row=i+20, column=1)
        button_browse_input_soil_key = tk.Button(master=second_frame, text="Browse",
                                                 font=self.MAIN_FONT, command=self.browse_input_soil_key). \
            grid(sticky="w", row=i+20, column=2)
        desc_input_soil_key = tk.Label(second_frame, text=self.DESC_INPUT_SOIL_KEY, font=self.DESC_FONT).\
            grid(sticky="w", row=i+21, column=0, columnspan=2)
        self.path_input_soil_key = tk.Label(master=second_frame, text=self.INPUT_SOIL_KEY, font=self.MAIN_FONT)
        self.path_input_soil_key.grid(sticky="w", row=i+22, column=0, columnspan=3)

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
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
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
        self.path_pyfluxpro_input_sheet.grid(sticky="w", row=i+13, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=i+14, column=0, columnspan=3)

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

    def browse_input_met(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
        self.path_input_met.config(text=filepath)
        self.INPUT_MET = filepath

    def browse_input_precip(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        self.path_input_precip.config(text=filepath)
        self.INPUT_PRECIP = filepath

    def browse_master_met(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        filepath = os.path.join(filepath, 'met_output.csv')
        self.path_master_met.config(text=filepath)
        self.MASTER_MET = filepath

    def browse_input_soil_key(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        self.path_input_soil_key.config(text=filepath)
        self.INPUT_SOIL_KEY = filepath

    def browse_eddypro_bin(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        self.path_eddypro_bin.config(text=filepath)
        self.EDDYPRO_BIN_LOC = filepath

    def browse_eddypro_proj_template(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        self.path_eddypro_proj_template.config(text=filepath)
        self.EDDYPRO_PROJ_FILE_TEMPLATE = filepath

    def browse_eddypro_proj_file_name(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.asksaveasfilename(initialdir=os.getcwd(),
                                                    title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        else:
            filepath = filedialog.asksaveasfilename(initialdir=filepath,
                                                    title="select a file", filetypes=[("eddypro files", "*.eddypro")])
        self.path_eddypro_proj_file_name.config(text=filepath)
        self.EDDYPRO_PROJ_FILE_NAME = filepath

    def browse_eddypro_proj_file(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("metadata files", "*.metadata")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("metadata files", "*.metadata")])
        self.path_eddypro_proj_file.config(text=filepath)
        self.EDDYPRO_PROJ_FILE = filepath

    def browse_eddypro_dyn_metadata(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
        self.path_eddypro_dyn_metadata.config(text=filepath)
        self.EDDYPRO_DYN_METADATA = filepath

    def browse_eddypro_output_path(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        self.path_eddypro_output_path.config(text=filepath)
        self.EDDYPRO_OUTPUT_PATH = filepath

    def browse_eddypro_input_ghg_path(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        self.path_eddypro_input_ghg_path.config(text=filepath)
        self.EDDYPRO_INPUT_GHG_PATH = filepath

    def browse_pyfluxpro_full_output(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        filepath = os.path.join(filepath, "full_output.csv")
        self.path_pyfluxpro_full_output.config(text=filepath)
        self.FULL_OUTPUT_PYFLUXPRO = filepath

    def browse_pyfluxpro_met_data(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        filepath = os.path.join(filepath, "Met_data_30.csv")
        self.path_pyfluxpro_met_data.config(text=filepath)
        self.MET_DATA_30_PYFLUXPRO = filepath

    def browse_pyfluxpro_input_sheet(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.asksaveasfilename(
                initialdir=os.getcwd(), title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        else:
            filepath = filedialog.asksaveasfilename(
                initialdir=filepath, title="select a file", filetypes=[("xlsx files", "*.xlsx")])
        self.path_pyfluxpro_input_sheet.config(text=filepath)
        self.PYFLUXPRO_INPUT_SHEET = filepath

    def save_env(self):
        user_conform_line = "USER_CONFIRMATION=" + self.combo_confirm.get()

        eddypro_input_title_line = "# input data for formatting EddyPro master meteorology data"
        eddypro_input_met_line = "INPUT_MET=" + self.INPUT_MET
        eddypro_input_precip_line = "INPUT_PRECIP=" + self.INPUT_PRECIP
        eddypro_missing_time_line = "MISSING_TIME=" + str(self.missing_time.get())
        eddypro_master_met_line = "MASTER_MET=" + self.MASTER_MET
        eddypro_input_soil_key_line = "INPUT_SOIL_KEY=" + self.INPUT_SOIL_KEY

        eddypro_run_title_line = "# input data for running EddyPro"
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

        pyfluxpro_title_line = "# PyFluxPro related data"
        pyfluxpro_full_output_line = "FULL_OUTPUT_PYFLUXPRO=" + self.FULL_OUTPUT_PYFLUXPRO
        pyfluxpro_met_data_line = "MET_DATA_30_PYFLUXPRO=" + self.MET_DATA_30_PYFLUXPRO
        pyfluxpro_input_sheet_line = "PYFLUXPRO_INPUT_SHEET=" + self.PYFLUXPRO_INPUT_SHEET

        lines = [
            user_conform_line,
            "",
            eddypro_input_title_line, eddypro_input_met_line, eddypro_input_precip_line,
            eddypro_missing_time_line, eddypro_master_met_line, eddypro_input_soil_key_line,
            "",
            eddypro_run_title_line, eddypro_bin_loc_line, eddypro_proj_template_line, eddypro_proj_file_name_line,
            eddypro_proj_title_line, eddypro_proj_id_line, eddypro_file_prototype_line, eddypro_proj_file_line,
            eddypro_dyn_metadata_line, eddypro_output_path_line, eddypro_input_ghg_path_line,
            "",
            pyfluxpro_title_line, pyfluxpro_full_output_line, pyfluxpro_met_data_line, pyfluxpro_input_sheet_line
        ]

        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

        answer = messagebox.askokcancel(title='Info', message="Would you like to save .env file?")
        if not answer:
            print("not saved.")
        else:
            with open(outfile, 'w') as f:
                for line in lines:
                    f.write(line)
                    f.write('\n')
                print("saved.")

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_click_user_confirm(self):
        tk.messagebox.showinfo("Info", self.INFO_USER_CONFIRMATION)

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


if __name__ == '__main__':
    app = EnvEditor()
