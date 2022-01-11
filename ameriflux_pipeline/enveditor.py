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
        self.SEPARATION_LABEL = "------------------------------------------------------------------------------------"
        self.SEPARATION_LABEL_SUB = "------------------"

        self.USER_CONFIRMATION_LABEL = "User confirmation"

        self.EDDYPRO_FORMAT_VARIABLE = "Variables for EddyPro formatting"
        self.BROWSE_INPUT_MET = "Input Meteorology Data"
        self.BROWSE_INPUT_PRECIP = "Input Precipitation Data"
        self.BROWSE_MASTER_MET = "Master Meteorology Data"
        self.BROWSE_INPUT_SOIL_KEY = "Input Soil Key"

        self.EDDYPRO_RUNNING_VARIABLE = "Variables for EddyPro running"
        self.BROWSE_EDDYPRO_BIN = "EddyPro Bin Folder"
        self.BROWSE_EDDYPRO_PROJ_FILE_NAME = "EddyPro Project File Path (select template folder)"
        self.BROWSE_EDDYPRO_PROJ_TITLE = "EddyPro Project Title"
        self.BROWSE_EDDYPRO_PROJ_ID = "EddyPro Project ID"
        self.BROWSE_EDDYPRO_FILE_PROTOTYPE = "EddyPro File Prototype"
        self.BROWSE_EDDYPRO_PROJ_FILE = "EddyPro Metadata File from GHG File"
        self.BROWSE_EDDYPRO_DYN_METADATA = "EddyPro Dynamic Metadata"
        self.BROWSE_EDDYPRO_OUTPUT_PATH = "EddyPro Output Path"
        self.BROWSE_EDDYPRO_INPUT_GHG_PATH = "EddyPro Input GHG Path"

        # PyFluxPro related data
        self.PYFLUXPROPRO_RUNNING_VARIABLE = "Variables for PyFluxPro running"
        self.BROWSE_FULL_OUTPUT_PYFLUXPRO="PyFluxPro Full Output (select folder)"
        self.BROWSE_MET_DATA_30_PYFLUXPRO="PyFluxPro Met Data 30 Output (select folder)"
        self.BROWSE_PYFLUXPRO_INPUT_SHEET="PyFluxPro Input Sheet Path (select folder)"

        self.SAVE_LABEL = "Save .env file"
        self.SAVE_ENV_FILE = "Save"

        # font variables
        self.MAIN_BOLD_FONT = "Times 14 bold"
        self.MAIN_FONT = "Times 11"
        self.BOLD_FONT = "Times 11 bold"

        # Load .env file
        load_dotenv()

        self.USER_CONFIRMATION = os.getenv('USER_CONFIRMATION')

        self.INPUT_MET = os.getenv('INPUT_MET')
        self.INPUT_PRECIP = os.getenv('INPUT_PRECIP')
        self.MISSING_TIME = os.getenv('MISSING_TIME')
        self.MASTER_MET = os.getenv('MASTER_MET')
        self.INPUT_SOIL_KEY = os.getenv('INPUT_SOIL_KEY')

        self.EDDYPRO_BIN_LOC = os.getenv('EDDYPRO_BIN_LOC')
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
        root.title("AmefiFlux Pipeline Environment Setter")
        root.geometry("600x400")

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
        self.main_canvas.bind('<Configure>', lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.main_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # create another frame inside the canvas
        second_frame = tk.Frame(self.main_canvas)

        # add that new frame to a window in the canvas
        self.main_canvas.create_window((0, 0), window=second_frame, anchor="nw")

        ########################################################
        # create user confirmation
        label_user_confirm = tk.Label(second_frame, text=self.USER_CONFIRMATION_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=0, column=0)
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=1, column=0)
        confirm_list = ("Y", "N", "A")
        confirm_list_index = 0
        for index, value in enumerate(confirm_list):
            if value == self.USER_CONFIRMATION:
                confirm_list_index = index
        n = tk.StringVar()
        self.combo_confirm = ttk.Combobox(second_frame)
        self.combo_confirm['values'] = confirm_list
        self.combo_confirm.current(confirm_list_index)
        self.combo_confirm.grid(sticky="w", row=2, column=0)

        #############################################################
        # create eddypro format main label
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=3, column=0)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=4, column=0)
        label_eddypro_format = tk.Label(master=second_frame, text=self.EDDYPRO_FORMAT_VARIABLE,
                                        font=self.MAIN_BOLD_FONT).grid(sticky="w", row=5, column=0)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=6, column=0)

        # create eddypro format input meteorology data
        label_input_met = tk.Label(master=second_frame, text=self.BROWSE_INPUT_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=7, column=0)
        button_browse_input_met = tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                                            command=self.browse_input_met). \
            grid(sticky="w", row=7, column=1)
        self.path_input_met = tk.Label(master=second_frame, text=self.INPUT_MET, font=self.MAIN_FONT)
        self.path_input_met.grid(sticky="w", row=8, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=9, column=0, columnspan=2)

        # create eddypro format input precipitation data
        label_input_precip = tk.Label(master=second_frame, text=self.BROWSE_INPUT_PRECIP, font=self.BOLD_FONT). \
            grid(sticky="w", row=10, column=0)
        button_browse_input_precip = tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                                               command=self.browse_input_precip). \
            grid(sticky="w", row=10, column=1)
        self.path_input_precip = tk.Label(master=second_frame, text=self.INPUT_PRECIP, font=self.MAIN_FONT)
        self.path_input_precip.grid(sticky="w", row=11, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=12, column=0, columnspan=2)

        # create eddypro format missing time
        missing_time_label = tk.Label(master=second_frame, text="Missing Time", font=self.BOLD_FONT). \
            grid(sticky="w", row=13, column=0, columnspan=2)
        self.missing_time = tk.Entry(master=second_frame, width=10, font=self.MAIN_FONT)
        self.missing_time.insert(0, self.MISSING_TIME)
        self.missing_time.grid(sticky="w", row=14, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=15, column=0, columnspan=2)

        # create eddypro format master met
        label_master_met = tk.Label(master=second_frame, text=self.BROWSE_MASTER_MET, font=self.BOLD_FONT). \
            grid(sticky="w", row=16, column=0)
        button_browse_input_master_met = tk.Button(master=second_frame, width=10, text="Browse",
                                                   font=self.MAIN_FONT, command=self.browse_master_met). \
            grid(sticky="w", row=16, column=1)
        self.path_master_met = tk.Label(master=second_frame, text=self.MASTER_MET, font=self.MAIN_FONT)
        self.path_master_met.grid(sticky="w", row=17, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=18, column=0, columnspan=2)

        # create eddypro format input soil key
        label_soil_key = tk.Label(master=second_frame, text=self.BROWSE_INPUT_SOIL_KEY, font=self.BOLD_FONT). \
            grid(sticky="w", row=19, column=0)
        button_browse_input_soil_key = tk.Button(master=second_frame, width=10, text="Browse",
                                                 font=self.MAIN_FONT, command=self.browse_input_soil_key). \
            grid(sticky="w", row=19, column=1)
        self.path_input_soil_key = tk.Label(master=second_frame, text=self.INPUT_SOIL_KEY, font=self.MAIN_FONT)
        self.path_input_soil_key.grid(sticky="w", row=20, column=0, columnspan=2)

        #############################################################
        # create eddypro run main title
        label_separation = tk.Label(master=second_frame, text=""). \
            grid(sticky="w", row=21, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=""). \
            grid(sticky="w", row=22, column=0, columnspan=2)
        label_b = tk.Label(master=second_frame, text=self.EDDYPRO_RUNNING_VARIABLE, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=23, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=24, column=0, columnspan=2)

        # create eddypro bin location
        label_eddypro_bin = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_BIN, font=self.BOLD_FONT). \
            grid(sticky="w", row=25, column=0)
        button_browse_eddypro_bin = tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                                              command=self.browse_eddypro_bin). \
            grid(sticky="w", row=25, column=1)
        self.path_eddypro_bin = tk.Label(master=second_frame, text=self.EDDYPRO_BIN_LOC, font=self.MAIN_FONT)
        self.path_eddypro_bin.grid(sticky="w", row=26, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=27, column=0, columnspan=2)

        # create eddypro project file
        label_eddypro_proj_file_name = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_FILE_NAME,
                     font=self.BOLD_FONT).grid(sticky="w", row=28, column=0)
        button_browse_eddypro_proj_file_name = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_proj_file_name).grid(sticky="w", row=28, column=1)
        self.path_eddypro_proj_file_name = \
            tk.Label(master=second_frame, text=self.EDDYPRO_PROJ_FILE_NAME, font=self.MAIN_FONT)
        self.path_eddypro_proj_file_name.grid(sticky="w", row=29, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=30, column=0, columnspan=2)

        # create eddypro project title
        eddypro_proj_title_label = tk.Label(master=second_frame, text="EddyPro Project Title",
                     font=self.BOLD_FONT).grid(sticky="w", row=31, column=0, columnspan=2)
        self.eddypro_proj_title = tk.Entry(master=second_frame, width=50, font=self.MAIN_FONT)
        self.eddypro_proj_title.insert(0, self.EDDYPRO_PROJ_TITLE)
        self.eddypro_proj_title.grid(sticky="w", row=32, column=0, columnspan=2)
        label_separation = \
            tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB).\
                grid(sticky="w", row=33, column=0, columnspan=2)

        # create eddypro project id
        eddypro_proj_id_label = tk.Label(master=second_frame, text="EddyPro Project ID", font=self.BOLD_FONT). \
            grid(sticky="w", row=34, column=0, columnspan=2)
        self.eddypro_proj_id = tk.Entry(master=second_frame, width=50, font=self.MAIN_FONT)
        self.eddypro_proj_id.insert(0, self.EDDYPRO_PROJ_ID)
        self.eddypro_proj_id.grid(sticky="w", row=35, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=36, column=0, columnspan=2)

        # create eddypro file prototype
        eddypro_file_prototype_label = \
            tk.Label(master=second_frame, text="EddyPro File Prototype", font=self.BOLD_FONT).\
                grid(sticky="w", row=37, column=0, columnspan=2)
        self.eddypro_file_prototype = tk.Entry(master=second_frame, width=50, font=self.MAIN_FONT)
        self.eddypro_file_prototype.insert(0, self.EDDYPRO_FILE_PROTOTYPE)
        self.eddypro_file_prototype.grid(sticky="w", row=38, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=39, column=0, columnspan=2)

        # create eddypro proj file that is metadata
        label_eddypro_proj_file = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_PROJ_FILE,
                                           font=self.BOLD_FONT).grid(sticky="w", row=40, column=0)
        button_browse_eddypro_proj_file = tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                                                    command=self.browse_eddypro_proj_file). \
            grid(sticky="w", row=40, column=1)
        self.path_eddypro_proj_file = tk.Label(master=second_frame, text=self.EDDYPRO_PROJ_FILE, font=self.MAIN_FONT)
        self.path_eddypro_proj_file.grid(sticky="w", row=41, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=42, column=0, columnspan=2)

        # create eddypro dynamic metedata
        label_eddypro_dyn_metadata = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_DYN_METADATA,
                                              font=self.BOLD_FONT).grid(sticky="w", row=43, column=0)
        button_browse_eddypro_dyn_metadata = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_dyn_metadata).grid(sticky="w", row=43, column=1)
        self.path_eddypro_dyn_metadata = tk.Label(master=second_frame, text=self.EDDYPRO_DYN_METADATA,
                                                  font=self.MAIN_FONT)
        self.path_eddypro_dyn_metadata.grid(sticky="w", row=44, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=45, column=0, columnspan=2)

        # create eddypro output path
        label_eddypro_output_path = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_OUTPUT_PATH,
                                             font=self.BOLD_FONT).grid(sticky="w", row=46, column=0)
        button_browse_eddypro_output_path = tk.Button(master=second_frame, width=10, text="Browse",
                                                      font=self.MAIN_FONT, command=self.browse_eddypro_output_path). \
            grid(sticky="w", row=46, column=1)
        self.path_eddypro_output_path = tk.Label(master=second_frame, text=self.EDDYPRO_OUTPUT_PATH,
                                                 font=self.MAIN_FONT)
        self.path_eddypro_output_path.grid(sticky="w", row=47, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=48, column=0, columnspan=2)

        # create eddypro input ghg path
        label_eddypro_input_ghg_path = tk.Label(master=second_frame, text=self.BROWSE_EDDYPRO_INPUT_GHG_PATH,
                                                font=self.BOLD_FONT).grid(sticky="w", row=46, column=0)
        button_browse_eddypro_input_ghg_path = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_eddypro_input_ghg_path).grid(sticky="w", row=46, column=1)
        self.path_eddypro_input_ghg_path = tk.Label(master=second_frame, text=self.EDDYPRO_INPUT_GHG_PATH,
                                                    font=self.MAIN_FONT)
        self.path_eddypro_input_ghg_path.grid(sticky="w", row=47, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=48, column=0, columnspan=2)

        #############################################################
        # create pyflux pro main title
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=49, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=50, column=0, columnspan=2)
        label_pyfluxpro = tk.Label(master=second_frame, text=self.PYFLUXPROPRO_RUNNING_VARIABLE,
                                   font=self.MAIN_BOLD_FONT).grid(sticky="w", row=51, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=52, column=0, columnspan=2)

        # create pyfluxpro full output
        label_pyfluxpro_full_output = tk.Label(master=second_frame, text=self.BROWSE_FULL_OUTPUT_PYFLUXPRO,
                                               font=self.BOLD_FONT).grid(sticky="w", row=53, column=0)
        button_browse_pyfluxpro_full_output = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_full_output).grid(sticky="w", row=53, column=1)
        self.path_pyfluxpro_full_output = tk.Label(master=second_frame, text=self.FULL_OUTPUT_PYFLUXPRO,
                                                   font=self.MAIN_FONT)
        self.path_pyfluxpro_full_output.grid(sticky="w", row=54, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=55, column=0, columnspan=2)

        # create pyfluxpro met data 30
        label_pyfluxpro_met_data = tk.Label(master=second_frame, text=self.BROWSE_MET_DATA_30_PYFLUXPRO,
                                            font=self.BOLD_FONT).grid(sticky="w", row=56, column=0)
        button_browse_pyfluxpro_met_data = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_met_data).grid(sticky="w", row=56, column=1)
        self.path_pyfluxpro_met_data = tk.Label(master=second_frame, text=self.MET_DATA_30_PYFLUXPRO, font=self.MAIN_FONT)
        self.path_pyfluxpro_met_data.grid(sticky="w", row=57, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=58, column=0, columnspan=2)

        # create pyfluxpro input sheet"
        label_pyfluxpro_input_sheet = tk.Label(master=second_frame, text=self.BROWSE_PYFLUXPRO_INPUT_SHEET,
                                               font=self.BOLD_FONT).grid(sticky="w", row=59, column=0)
        button_browse_pyfluxpro_input_sheet = \
            tk.Button(master=second_frame, width=10, text="Browse", font=self.MAIN_FONT,
                      command=self.browse_pyfluxpro_input_sheet).grid(sticky="w", row=59, column=1)
        self.path_pyfluxpro_input_sheet = tk.Label(master=second_frame, text=self.PYFLUXPRO_INPUT_SHEET,
                                              font=self.MAIN_FONT)
        self.path_pyfluxpro_input_sheet.grid(sticky="w", row=60, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame,
                                    text=self.SEPARATION_LABEL_SUB).grid(sticky="w", row=61, column=0, columnspan=2)

        #############################################################
        # create save frame
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=80, column=0, columnspan=2)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=81, column=0, columnspan=2)
        label_eddypro_save = tk.Label(master=second_frame, text=self.SAVE_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=82, column=0, columnspan=2)
        button_save_env = tk.Button(master=second_frame, width=25, text=self.SAVE_ENV_FILE, font=self.MAIN_FONT,
                                    command=self.save_env).grid(sticky="w", row=83, column=0, columnspan=2)

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
            filepath = filedialog.askopenfilename(initialdir=os.getcwd(),
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
        else:
            filepath = filedialog.askopenfilename(initialdir=filepath,
                                                  title="select a file", filetypes=[("csv files", "*.csv")])
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

    def browse_eddypro_proj_file_name(self):
        filepath = tk.StringVar()
        if filepath == "":
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        filepath = os.path.join(filepath, "EddyPro_Run_Template.eddypro")
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
            filepath = filedialog.askdirectory(initialdir=os.getcwd())
        else:
            filepath = filedialog.askdirectory(initialdir=filepath)
        filepath = os.path.join(filepath, "Met_data_30.csv")
        self.path_pyfluxpro_input_sheet.config(text=filepath)
        self.PYFLUXPRO_INPUT_SHEET = filepath

    def save_env(self):
        print(self.combo_confirm.get())
        print(self.INPUT_MET)
        print(self.INPUT_PRECIP)
        print(self.missing_time.get())
        print(self.MASTER_MET)
        print(self.INPUT_SOIL_KEY)
        print(self.EDDYPRO_BIN_LOC)
        print(self.EDDYPRO_PROJ_FILE_NAME)
        print(self.eddypro_proj_title.get())
        print(self.eddypro_proj_id.get())
        print(self.eddypro_file_prototype.get())
        print(self.EDDYPRO_PROJ_FILE)
        print(self.EDDYPRO_DYN_METADATA)
        print(self.EDDYPRO_OUTPUT_PATH)
        print(self.EDDYPRO_INPUT_GHG_PATH)
        print(self.FULL_OUTPUT_PYFLUXPRO)
        print(self.MET_DATA_30_PYFLUXPRO)
        print(self.PYFLUXPRO_INPUT_SHEET)

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")


if __name__ == '__main__':
    app = EnvEditor()
