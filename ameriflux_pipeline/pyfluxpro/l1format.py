import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import os

import warnings
warnings.filterwarnings("ignore")

class L1Format:
    """
    Class to implement formatting of PyFluxPro L1 control file as per AmeriFlux standards
    """
    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L1
    LEVEL_LINE = "level = L1"  # set the level

    # main method which calls other functions
    @staticmethod
    def data_formatting(pyfluxpro_input, l1_input, l1_output, ameriflux_mainstem_key, soils_key,
                        spaces=SPACES, level_line=LEVEL_LINE):
        """
        Main method for the class.

        Args:
            pyfluxpro_input (str): A file path for the PyFluxPro input excel sheet formatted for Ameriflux
            l1_input (str): A file path for the input L1.txt. This is the PyFluxPro original L1 control file
            l1_output (str): A file path for the output L1.txt.
                            This is the PyFluxPro L1 control file formatted for AmeriFlux
            ameriflux_mainstem_key (str): Variable name key used to match the original variable names to Ameriflux names
                                            This is an excel file named Ameriflux-Mainstem-Key.xlsx
            soils_key (str): A file path for input soil key sheet. This is used to match the original and
                                AmeriFlux variable names
            spaces (str): Spaces to be inserted before each section and line
            level_line (str): Line specifying the level. L1 for this section.
        Returns:
            obj: Pandas DataFrame object.
        """
        # open input file in read mode
        l1 = open(l1_input, 'r')
        # open output file in write mode
        l1_output = open(l1_output, 'w+')
        l1_output_lines = []  # comma separated list of lines to be written
        # read lines from l1_input
        l1_lines = l1.readlines()

        # write the level line
        l1_output_lines.append(level_line.strip())

        # write Files section
        files_lines = []
        files_lines.append("[Files]")
        filename = os.path.basename(pyfluxpro_input)
        file_path = os.path.dirname(pyfluxpro_input)
        out_filename = os.path.basename(l1_output)

        file_path_line = spaces + "file_path = " + file_path
        files_lines.append(file_path_line)
        in_filename_line = spaces + "in_filename = " + filename
        files_lines.append(in_filename_line)
        in_headerrow_line = spaces + "in_headerrow = " + '1'
        files_lines.append(in_headerrow_line)
        in_firstdatarow_line = spaces + "in_firstdatarow = " + '3'
        files_lines.append(in_firstdatarow_line)
        out_filename_line = spaces + "out_filename = " + out_filename
        files_lines.append(out_filename_line)
        # write lines to l1 output
        l1_output_lines.extend(files_lines)

        # get Global section
        global_lines, variable_ind = L1Format.get_global_lines(l1_lines, spaces)
        # write global section lines to l1 output
        l1_output_lines.extend(global_lines)

        # write the variables section to dataframe. this is used to get the indexes easily
        df = pd.DataFrame(l1_lines[variable_ind + 1:], columns=['Text'])
        df['Text'] = df['Text'].apply(lambda x: x.strip())  # remove newline and extra spaces from each line
        variables, var_start_end = L1Format.get_variables(df)

        ameriflux_key = pd.read_excel(ameriflux_mainstem_key)  # read AmeriFlux-Mainstem variable name matching file
        df = L1Format.format_variables(df, var_start_end, ameriflux_key)



    @staticmethod
    def get_global_lines(lines, spaces):
        """
            Get Global section from L1.txt

            Args:
                lines (list): List of the strings that are read fom L1.txt
                spaces (str): Spaces to be inserted before each section and line

            Returns:
                global_lines (list): List of strings to be written to l1_output
                ind (integer): Index of [[Variables]] section
        """
        global_lines = []
        global_start_writing = False  # flag to check if Global section is over
        for ind, line in enumerate(lines):
            if line.strip() == "[Global]":
                global_lines.append(line.strip())
                global_start_writing = True
            if global_start_writing:
                if line.strip() == "[Variables]":
                    global_start_writing = False
                    return global_lines, ind
                global_lines.append(spaces + line.strip())


    @staticmethod
    def get_variables(df):
        """
            Get all variables and start and end index for each variable from L1.txt

            Args:
                df (obj): Pandas dataframe with all variable lines from L1.txt
            Returns:
                variables (obj) : Pandas dataframe. This is a subset of the input dataframe with only variable names
                var_start_end (list): List of tuple, the starting and ending index for each variable
        """
        var_pattern = "^\[\[[a-zA-Z0-9_]+\]\]$"
        variables = df[df['Text'].str.contains(var_pattern)]
        var_start_end = []
        for i in range(len(variables.index) - 1):
            start_ind = variables.index[i]
            end_ind = variables.index[i + 1]
            var_start_end.append((start_ind, end_ind))
        return variables, var_start_end


    @staticmethod
    def format_variables(df, var_start_end, ameriflux_key):
        """
            Change variable names and units to AmeriFlux standard

            Args:
                df (obj): Pandas dataframe with all variable lines from L1.txt
                var_start_end (list): List of tuple, the starting and ending index for each variable
                ameriflux_key (obj): Pandas dataframe of AmeriFlux-Mainstem varible name sheet
            Returns:
                df (obj) : Pandas dataframe variable formatted for AmeriFlux
        """
        for start, end in var_start_end:
            # get each variable in a separate df
            var = df[start:end]
            # get the [[[xl]]] section
            xl_pattern = "^\[\[\[xl\]\]\]$"
            xl = var[var['Text'].str.contains(xl_pattern)]
            xl_df = df[xl.index[0]:end]
            # get the [[[Attr]]] OR [[[attr]]] section
            attr_pattern = "^\[\[\[Attr\]\]\]$|^\[\[\[attr\]\]\]$"
            attr = var[var['Text'].str.contains(attr_pattern)]
            attr_df = df[attr.index[0]:xl.index[0]]

            name_row = xl_df[xl_df['Text'].apply(lambda x: x.startswith("name"))]
            units_row = attr_df[attr_df['Text'].apply(lambda x: x.startswith("units"))]

            if name_row.shape[0] > 0:
                # if name row exists, check if var name should be changed for Ameriflux
                var_name_index = name_row.index[0]
                var_org_name = name_row['Text'].iloc[0].split('=')[1].strip()
                if ameriflux_key['Input sheet variable name'].str.contains(var_org_name).any():
                    var_ameriflux_name = ameriflux_key.loc[ameriflux_key['Input sheet variable name'] == var_org_name,
                                                           'Ameriflux variable name'].iloc[0]
                    var['Text'].iloc[var_name_index] = "name = " + var_ameriflux_name

                    if units_row.shape[0] > 0:
                        var_units_index = units_row.index[0]
                        var_ameriflux_units = \
                            ameriflux_key.loc[ameriflux_key['Input sheet variable name'] == var_org_name,
                                              'Units after formatting'].iloc[0]
                        if len(var_ameriflux_units) > 0:
                            # replace units only if it needs to be changed
                            var['Text'].iloc[var_units_index] = "units = " + var_ameriflux_units
                # update the original dataframe with modified variable name and unit
                df.update(var)

        return df


    @staticmethod
    def save_string_list_to_file(in_list, outfile):
        """
            Save list with string to a file

            Args:
                in_list (list): List of the strings that are the eddypro project file elements
                outfile (str): A file path of the output file

            Returns:
                None
        """
        try:
            with open(outfile, 'w') as f:
                f.write('\n'.join(in_list))
        except Exception:
            raise Exception("Failed to create temporary project file")