# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import tkinter as tk

from tkinter import ttk as ttk
from tkinter import messagebox

import utils.data_util as data_util
import pre_pyfluxpro as prepy
import post_pyfluxpro as postpy


class Pipeline:
    def __init__(self):
        self.OS_PLATFORM = data_util.get_platform()

        # text variables
        self.SEPARATION_LABEL = "---------------------------------------------------------"
        self.SEPARATION_LABEL_SUB = "------------------"
        self.INFO_TITLE = "info"

        self.LINE_PRE_PYFLUXPRO = 4
        self.LINE_POST_PYFLUXPRO = 10
        self.LINE_EDDYPRO_PREPROCESSING = 18
        self.LINE_EDDYPRO_RUN = 24
        self.LINE_RUN_AMERIFLUX_PROCESSING = 30

        # font variables
        self.MAIN_BOLD_FONT = "Times 14 bold"
        self.MAIN_FONT = "Times 11"
        self.BOLD_FONT = "Times 11 bold"
        self.DESC_FONT = "Times 10 italic"

        # run messages
        self.PRE_PYFLUXPRO_SUCCESS = "Pre pyfluxpro process run has finished successfully."
        self.PRE_PYFLUXPRO_FAIL = "Pre pyfluxpro process run has failed."
        self.POST_PYFLUXPRO_SUCCESS = "Post pyfluxpro process run has finished successfully."
        self.POST_PYFLUXPRO_FAIL = "Post pyfluxpro process run has failed."
        self.EDDYPRO_PREP_SUCCESS = "EddyPro data preparation process has finished successfully."
        self.EDDYPRO_PREP_FAIL = "EddyPro data preparation process has failed."
        self.EDDYPRO_SUCCESS = "Running EddyPro has finished successfully."
        self.EDDYPRO_FAIL = "Running EddyPro has failed."
        self.PYFLUXPRO_SUCCESS = "Pyfluxpro data preparation process has finished successfully."
        self.PYFLUXPRO_FAIL = "Pyfluxpro data preparation process has failed."

        # other variables
        self.MAIN_TITLE = " Run Pipeline"
        self.DESC_MAIN_PROCESS = " All variables used are from .env file. To set the variables use enveditor" \
                                 " Please check the terminal or log file for program logs"
        self.INFO_OUT_DATA_GENERATED = "Output meteorology data has been generated."
        self.WORKING_DIRECTORY = ""

        # Run Pre PyFluxPro
        self.RUN_PRE_PYFLUXPRO = "Run pre PyfluxPro process"
        self.DESC_PRE_PYFLUXPRO = " run whole pre pyfluxpro pipeline."
        self.INFO_PRE_PYFLUXPRO = "This will run whole pre pyfluxpro pipeline process, " \
                                  "including eddypro run and input files for pyfluxpro."

        # Run Post PyFluxPro
        self.RUN_POST_PYFLUXPRO = "Run post PyfluxPro process"
        self.DESC_POST_PYFLUXPRO = " run whole post pyfluxpro pipeline."
        self.INFO_POST_PYFLUXPRO = "This will run whole post pyfluxpro pipeline process, " \
                                   "including the generation of AmeriFlux site submission file."

        # Run Eddypro data processor
        self.RUN_EDDYPRO_PROCESSOR = "Run EddyPro data preparation"
        self.DESC_EDDYPRO_PROCESSOR = " run eddypro data preparation process."
        self.INFO_EDDYPRO_PROCESSOR = "This will run eddypro data preparation process that will " \
                                      "needed for running the eddypro."

        # Run Eddypro
        self.RUN_EDDYPRO = "Run EddyPro application"
        self.DESC_EDDYPRO_RUN = " run eddypro application."
        self.INFO_EDDYPRO_RUN = "This will run eddypro application with given datasets."

        # PyFluxPro data preparation
        self.RUN_PYFLUXPRO = "Run PyFluxPro data preparation"
        self.DESC_PYFLUXPRO = " run pypluxpro data prepartion."
        self.INFO_PYFLUXPRO = "This will run pyfluxpro data preparation process for running pyfluxpro."

    def run(self):
        # create main gui window
        root = tk.Tk()
        root.title("Ameriflux Pipeline Modular Runs")
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
        # create main title
        label_main_title = tk.Label(second_frame, text=self.MAIN_TITLE, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i, columnspan=3)
        desc_main = tk.Label(second_frame, text=self.DESC_MAIN_PROCESS, font=self.DESC_FONT). \
            grid(sticky="w", row=i+1, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text=self.SEPARATION_LABEL).grid(sticky="w", row=i+2, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+3, columnspan=3)

        ##################################################
        # create pre pyfluxpro
        i = self.LINE_PRE_PYFLUXPRO
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)

        label_pre_pyfluxpro = tk.Label(master=second_frame, text=self.RUN_PRE_PYFLUXPRO, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i+1, column=0, columnspan=3)
        desc_pre_pyfluxpro = tk.Label(second_frame, text=self.DESC_PRE_PYFLUXPRO, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        info_pre_pyfluxpro = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                       command=self.on_click_pre_pyfluxpro). \
            grid(sticky="w", row=i+3, column=0)
        button_run_pre_pyfluxpro = tk.Button(
            master=second_frame, width=25, text="Run", font=self.MAIN_FONT,
            command=self.run_pre_pyfluxpro).grid(sticky="w", row=i+3, column=1, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+5, columnspan=3)

        ##################################################
        # create post pyfluxpro
        i = self.LINE_POST_PYFLUXPRO
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)

        label_post_pyfluxpro = tk.Label(master=second_frame, text=self.RUN_POST_PYFLUXPRO, font=self.MAIN_BOLD_FONT). \
            grid(sticky="w", row=i+1, column=0, columnspan=3)
        desc_post_pyfluxpro = tk.Label(second_frame, text=self.DESC_POST_PYFLUXPRO, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        info_post_pyfluxpro = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                        command=self.on_click_post_pyfluxpro). \
            grid(sticky="w", row=i+3, column=0)
        button_run_post_pyfluxpro = tk.Button(master=second_frame, width=25, text="Run", font=self.MAIN_FONT,
                                              command=self.run_post_pyfluxpro).grid(sticky="w", row=i+3,
                                                                                    column=1, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+5, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+6, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+7, column=0, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+8, column=0, columnspan=3)

        ##################################################
        # create eddypro data preparation
        i = self.LINE_EDDYPRO_PREPROCESSING
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)

        label_eddypro_process = tk.Label(master=second_frame, text=self.RUN_EDDYPRO_PROCESSOR,
                                         font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+1, column=0, columnspan=3)
        desc_eddypro_process = tk.Label(second_frame, text=self.DESC_EDDYPRO_PROCESSOR, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        info_eddypro_process = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                         command=self.on_click_eddypro_process). \
            grid(sticky="w", row=i+3, column=0)
        button_run_eddypro_process = tk.Button(master=second_frame, width=25, text="Run", font=self.MAIN_FONT,
                                               command=self.run_eddypro_processing).grid(sticky="w", row=i+3,
                                                                                         column=1, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+5, columnspan=3)

        ##################################################
        # run eddypro
        i = self.LINE_EDDYPRO_RUN
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)

        label_eddypro_run = tk.Label(master=second_frame, text=self.RUN_EDDYPRO,
                                     font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+1, column=0, columnspan=3)
        desc_eddypro_run = tk.Label(second_frame, text=self.DESC_EDDYPRO_RUN, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        info_eddypro_run = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                     command=self.on_click_eddypro_run). \
            grid(sticky="w", row=i+3, column=0)
        button_run_eddypro_run = tk.Button(master=second_frame, width=25, text="Run", font=self.MAIN_FONT,
                                           command=self.run_eddypro).grid(sticky="w", row=i+3, column=1, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+5, columnspan=3)

        ##################################################
        # run pyfluxpro preparation
        i = self.LINE_RUN_AMERIFLUX_PROCESSING
        label_separation = tk.Label(master=second_frame, text="").grid(sticky="w", row=i, column=0, columnspan=3)

        label_pyfluxpro = tk.Label(master=second_frame, text=self.RUN_PYFLUXPRO,
                                   font=self.MAIN_BOLD_FONT).grid(sticky="w", row=i+1, column=0, columnspan=3)
        desc_pyfluxpro = tk.Label(second_frame, text=self.DESC_PYFLUXPRO, font=self.DESC_FONT). \
            grid(sticky="w", row=i+2, column=0, columnspan=3)
        info_pyfluxpro = tk.Button(second_frame, text=self.INFO_TITLE, font=self.MAIN_FONT,
                                   command=self.on_click_pyfluxpro). \
            grid(sticky="w", row=i+3, column=0)
        button_run_pyfluxpro = tk.Button(master=second_frame, width=25, text="Run", font=self.MAIN_FONT,
                                         command=self.run_pyfluxpro).grid(sticky="w", row=i+3, column=1, columnspan=3)
        label_separation = tk.Label(master=second_frame, text=self.SEPARATION_LABEL). \
            grid(sticky="w", row=i+4, column=0, columnspan=3)
        label_separation = tk.Label(second_frame, text="").grid(sticky="w", row=i+5, columnspan=3)

        root.mainloop()

    def _on_mousewheel(self, event):
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_click_pre_pyfluxpro(self):
        tk.messagebox.showinfo("Info", self.INFO_PRE_PYFLUXPRO)

    def on_click_post_pyfluxpro(self):
        tk.messagebox.showinfo("Info", self.INFO_POST_PYFLUXPRO)

    def on_click_eddypro_process(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_PROCESSOR)

    def on_click_eddypro_run(self):
        tk.messagebox.showinfo("Info", self.INFO_EDDYPRO_RUN)

    def on_click_pyfluxpro(self):
        tk.messagebox.showinfo("Info", self.RUN_PYFLUXPRO)

    def run_pre_pyfluxpro(self):
        is_success = prepy.run()
        if is_success:
            tk.messagebox.showinfo("Info", self.PRE_PYFLUXPRO_SUCCESS)
        else:
            tk.messagebox.showerror("Error", self.PRE_PYFLUXPRO_FAIL)

    def run_post_pyfluxpro(self):
        is_success = postpy.run()
        if is_success:
            tk.messagebox.showinfo("Info", self.POST_PYFLUXPRO_SUCCESS)
        else:
            tk.messagebox.showerror("Error", self.POST_PYFLUXPRO_FAIL)

    def run_eddypro_processing(self):
        is_success = prepy.run(2)
        if is_success:
            tk.messagebox.showinfo("Info", self.EDDYPRO_PREP_SUCCESS)
        else:
            tk.messagebox.showerror("Error", self.EDDYPRO_PREP_FAIL)

    def run_eddypro(self):
        is_success = prepy.run(3)
        if is_success:
            tk.messagebox.showinfo("Info", self.EDDYPRO_SUCCESS)
        else:
            tk.messagebox.showerror("Error", self.EDDYPRO_FAIL)

    def run_pyfluxpro(self):
        is_success = prepy.run(4)
        if is_success:
            tk.messagebox.showinfo("Info", self.PYFLUXPRO_SUCCESS)
        else:
            tk.messagebox.showerror("Error", self.PYFLUXPRO_FAIL)


if __name__ == '__main__':
    app = Pipeline()
    app.run()
