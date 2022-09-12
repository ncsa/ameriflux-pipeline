# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made availabel under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is availabel at https://www.mozilla.org/en-US/MPL/2.0/

import os
import tkinter as tk
import datetime
import met_data_merge as mm

from tkinter import ttk as ttk
from tkinter import filedialog, messagebox
from tkcalendar import Calendar

from eddypro.runeddypro import RunEddypro


class MetMergerGUI():
    def __init__(self):
        self.INPUT_DATA = []
        self.INPUT_DATA_STR = ""
        self.OUT_DATA = ""
        self.START_DATE = ""
        self.END_DATE = ""

        self.OS_PLATFORM = RunEddypro.get_platform()

        # text variables
        self.SEPARATION_LABEL = "---------------------------------------------------------"
        self.SEPARATION_LABEL_SUB = "------------------"
        self.INFO_TITLE = "info"

        self.LINE_START_DATE = 2
        self.LINE_END_DATE = 6
        self.LINE_IN_DATA = 10
        self.LINE_OUT_DATA = 15 + len(self.INPUT_DATA)
        self.LINE_CREATE = 20 + len(self.INPUT_DATA)

        # font variables
        self.MAIN_BOLD_FONT = "Times 14 bold"
        self.MAIN_FONT = "Times 11"
        self.BOLD_FONT = "Times 11 bold"
        self.DESC_FONT = "Times 10 italic"

        # other variables
        self.MAIN_TITLE = " Merge Met Data"
        self.IS_CALENDAR_START = True
        self.ERROR_DATE = "The end date is earlier than start date."
        self.ERROR_IN_DATE = "No input data has been selected."
        self.INFO_OUT_DATA_GENERATED = "Output meteorology data has been generated."
        self.WORKING_DIRECTORY = ""

        # start date
        self.START_DATE_LOCAL_VALUE = ""
        self.LABEL_START_DATE = " Set start date"
        self.DESC_START_DATE = " start date for the output Mmteorology data."
        self.INFO_START_DATE = "The date will be used as the start date for the output meteorology data."

        # end date
        self.END_DATE_LOCAL_VALUE = ""
        self.LABEL_END_DATE = " Set end date"
        self.DESC_END_DATE = " end date for the output meteorology data."
        self.INFO_END_DATE = "The date will be used as the end date for the output meteorology data."

        # input data
        self.LABEL_INPUT_DATA = " Select input data"
        self.BROWSE_INPUT_DATA = " input meteorology data."
        self.DESC_INPUT_DATA = " input meteorology data."
        self.INFO_INPUT_DATA = "The date will be used for creating the output meteorology data."

        # out data
        self.BROWSE_OUTPUT_PATH = " Output meteorology data"
        self.DESC_OUTPUT_PATH = " output meteorology data after all input data get merged."
        self.INFO_OUTPUT_PATH = "The output meteorology data after all input data get merged from start to end date"

        # create button
        self.SAVE_LABEL = "Generate output meteorology data"
        self.SAVE_ENV_FILE = "Generate"

    def run(self):
        # create main gui window
        root = tk.Tk()
        root.title("AmeriFlux Pipeline Environment Setter")
        root.geometry("800x800")

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

        i = 0
        # create start date
        label_main_title = tk.Label(second_frame, text=self.MAIN_TITLE, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i, columnspan=3)
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+1, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+2, columnspan=3)

        ##################################################
        # start date
        i = self.LINE_START_DATE
        title_start_date = tk.Label(second_frame, text=self.LABEL_START_DATE, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+1, column=0)
        button_info_start_date = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_start_date). \
            grid(sticky="w", row=i+1, column=1)
        button_set_start_date = tk.Button(second_frame, text=self.LABEL_START_DATE,
                                          command=self.pop_up_calendar_start).grid(sticky="w", row=i+1, column=2)
        desc_start_date = tk.Label(second_frame, text=self.DESC_START_DATE, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, columnspan=3)
        self.start_date_value = tk.Label(
            master=second_frame, text=self.START_DATE_LOCAL_VALUE, font=self.MAIN_FONT)
        self.start_date_value.grid(sticky="w", row=i+3, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)

        ##################################################
        # end date
        i = self.LINE_END_DATE
        title_end_date = tk.Label(second_frame, text=self.LABEL_END_DATE, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+1, column=0)
        button_info_end_date = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_end_date). \
            grid(sticky="w", row=i+1, column=1)
        button_set_end_date = tk.Button(second_frame, text=self.LABEL_END_DATE, command=self.pop_up_calendar_end). \
            grid(sticky="w", row=i+1, column=2)
        desc_start_date = tk.Label(second_frame, text=self.DESC_END_DATE, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, columnspan=3)
        self.end_date_value = tk.Label(
            master=second_frame, text=self.END_DATE_LOCAL_VALUE, font=self.MAIN_FONT)
        self.end_date_value.grid(sticky="w", row=i+3, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)

        ##################################################
        # create input data list
        i = self.LINE_IN_DATA
        label_input_data = tk.Label(master=second_frame, text=self.BROWSE_INPUT_DATA, font=self.BOLD_FONT). \
            grid(sticky="w", row=i+1, column=0)
        button_info_input_data = tk.Button(second_frame, text=self.INFO_TITLE, command=self.on_click_input_data). \
            grid(sticky="w", row=i+1, column=1)
        button_browse_input_data = tk.Button(master=second_frame, text="Add file",
                                             font=self.MAIN_FONT, command=self.browse_input_path). \
            grid(sticky="w", row=i+1, column=2)
        button_reset_input_data = tk.Button(master=second_frame, text="Reset",
                                            font=self.MAIN_FONT, command=self.reset_input_path). \
            grid(sticky="w", row=i+2, column=0)
        desc_input_data = tk.Label(second_frame, text=self.DESC_INPUT_DATA, font=self.DESC_FONT). \
            grid(sticky="w", row=i+3, column=0, columnspan=2)
        self.path_input_data = tk.Label(master=second_frame, text=self.INPUT_DATA_STR, font=self.MAIN_FONT)
        self.path_input_data.grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+5+len(self.INPUT_DATA), column=0, columnspan=3)

        ##################################################
        # out met data
        i = self.LINE_OUT_DATA
        label_output_path = tk.Label(master=second_frame, text=self.BROWSE_OUTPUT_PATH,
                                     font=self.BOLD_FONT).grid(sticky="w", row=i+1, column=0)
        info_output_path = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                     command=self.on_click_output_path). \
            grid(sticky="w", row=i+1, column=1)
        button_browse_output_path = tk.Button(master=second_frame, text="Browse",
                                              font=self.MAIN_FONT, command=self.browse_output_path). \
            grid(sticky="w", row=i+1, column=2)
        desc_output_path = tk.Label(second_frame, text=self.DESC_OUTPUT_PATH, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        self.path_output_path = tk.Label(master=second_frame, text=self.OUT_DATA, font=self.MAIN_FONT)
        self.path_output_path.grid(sticky="w", row=i+3, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL_SUB). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)

        #############################################################
        # create button
        i = self.LINE_CREATE
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_eddypro_save = tk.Label(master=second_frame, text=self.SAVE_LABEL, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        button_save_env = tk.Button(master=second_frame, width=25, text=self.SAVE_ENV_FILE, font=self.MAIN_FONT,
                                    command=self.create_output).grid(sticky="w", row=i+3, column=0, columnspan=3)

        root.mainloop()

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_click_start_date(self):
        tk.messagebox.showinfo("Info", self.INFO_START_DATE)

    def on_click_end_date(self):
        tk.messagebox.showinfo("Info", self.INFO_END_DATE)

    def on_click_input_data(self):
        tk.messagebox.showinfo("Info", self.INFO_END_DATE)

    def on_click_output_path(self):
        tk.messagebox.showinfo("Info", self.INFO_OUTPUT_PATH)

    def browse_input_path(self):
        filepath = self.WORKING_DIRECTORY
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.askopenfilename(
            initialdir=initialdir, title="select a file")
        if filepath != "":
            self.INPUT_DATA.append(filepath)
            input_data_str = self.construct_input_data_str()
            self.path_input_data.config(text=input_data_str)
            self.WORKING_DIRECTORY = filepath

    def construct_input_data_str(self):
        input_data_str = ""

        for i in range(len(self.INPUT_DATA)):
            if i == 0:
                input_data_str = self.INPUT_DATA[i] + "\n"
            else:
                input_data_str = input_data_str + self.INPUT_DATA[i] + "\n"

        return input_data_str

    def reset_input_path(self):
        self.INPUT_DATA_STR = ""
        self.INPUT_DATA = []
        self.path_input_data.config(text="")

    def browse_output_path(self):
        filepath = self.WORKING_DIRECTORY
        initialdir = os.getcwd() if filepath == "" else filepath
        filepath = filedialog.asksaveasfilename(
            initialdir=initialdir, title="select a file", filetypes=[("csv files", "*.csv")])
        if filepath != "":
            filepath = self.check_extension_and_add(filepath, ".csv")
            self.path_output_path.config(text=filepath)
            self.OUT_DATA = filepath
            self.WORKING_DIRECTORY = filepath

    def pop_up_calendar_start(self):
        self.IS_CALENDAR_START = True
        self.pop_up_calendar()

    def pop_up_calendar_end(self):
        self.IS_CALENDAR_START = False
        self.pop_up_calendar()

    def pop_up_calendar(self):
        cal_root = tk.Tk()

        # Set geometry
        cal_root.geometry("400x400")

        # Add Calendar
        cal = Calendar(cal_root, selectmode='day', year=2021, month=1, day=1)
        cal.pack(pady=20)

        def pick_date():
            if self.IS_CALENDAR_START:
                self.START_DATE = cal.get_date()
                if cal.get_date() != "":
                    self.start_date_value.config(text=cal.get_date())
                cal_root.destroy()
            else:
                self.END_DATE = cal.get_date()
                if cal.get_date() != "":
                    self.end_date_value.config(text=cal.get_date())
                cal_root.destroy()

        # Add Button and Label
        tk.Button(cal_root, text="Set Date", command=pick_date).pack(pady=20)

        # Execute Tkinter
        cal_root.mainloop()

    def check_extension_and_add(self, instring, extension):
        # parset the extension
        filename, file_extension = os.path.splitext(instring)
        if file_extension.lower() != extension.lower():
            # add given extension to the end of the string
            instring = instring + extension

        return instring

    def create_output(self):
        is_date_error = False
        is_in_data_error = False
        is_output_error = False

        # convert start time
        if self.START_DATE != "":
            start_date = datetime.datetime.strptime(self.START_DATE, '%m/%d/%y').strftime('%Y-%m-%d')

        # convert end date
        if self.END_DATE != "":
            end_date = datetime.datetime.strptime(self.END_DATE, '%m/%d/%y').strftime('%Y-%m-%d')

        # check if start and end date are in correct period
        if self.START_DATE == "" or self.END_DATE == "":
            is_date_error = True
            tk.messagebox.showerror("ERROR", "Please set start or end date")
        else:
            is_date_error = False

        if not is_date_error:
            if (start_date >= end_date):
                is_date_error = True
                tk.messagebox.showerror("Error", self.ERROR_DATE)
            else:
                is_date_error = False

        # check if there is any input data
        if not is_date_error:
            if len(self.INPUT_DATA) == 0:
                is_in_data_error = True
                tk.messagebox.showerror("Error", self.ERROR_IN_DATE)
            else:
                is_in_data_error = False

            # create in data string
            in_data_str = ""
            for i in range(len(self.INPUT_DATA)):
                if i == 0:
                    in_data_str = self.INPUT_DATA[i] + ","
                elif i == len(self.INPUT_DATA) - 1:
                    in_data_str = in_data_str + self.INPUT_DATA[i]
                else:
                    in_data_str = in_data_str + self.INPUT_DATA[i] + ","

            # check if there is output selected
            if not is_in_data_error:
                if self.OUT_DATA == "":
                    is_output_error = True
                    tk.messagebox.showerror("Error", "No output data has been selected")
                else:
                    is_output_error = False

                # create final output
                if not is_output_error:
                    files = list(set(self.INPUT_DATA))
                    # check if file exists
                    is_valid = mm.validate_inputs(files, start_date, end_date, self.OUT_DATA)
                    if is_valid:
                        mm.main(files, start_date, end_date, self.OUT_DATA)
                        tk.messagebox.showinfo("INFO", self.INFO_OUT_DATA_GENERATED)
                    else:
                        tk.messagebox.showerror("ERROR", "Inputs are not valid. Data merge failed. Aborting")


if __name__ == '__main__':
    app = MetMergerGUI()
    app.run()
