import pandas as pd
import os
import re

import utils.data_util as data_util


class L2Format:
    """
    Class to implement formatting of PyFluxPro L2 control file as per AmeriFlux standards
    """
    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L2
    LEVEL_LINE = "level = L2"  # set the level
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]$'  # variable name pattern

    # main method which calls other functions
    @staticmethod
    def data_formatting(pyfluxpro_ameriflux_labels, l2_mainstem, l2_ameriflux_only, l1_run_output, l2_run_output,
                        l2_ameriflux_output, spaces=SPACES, level_line=LEVEL_LINE):
        """
        Main method for the class.

        Args:
            pyfluxpro_ameriflux_labels (dict): Mapping of pyfluxpro-friendly label to Ameriflux-friendly labels for
                                            variables in l1_ameriflux_output
            l2_mainstem (str): A file path for the input L2.txt. This is the PyFluxPro original L2 control file
            l2_ameriflux_only (str): A file path for the L2.txt that contains only Ameriflux-friendly variables
            l1_run_output (str): A file path for the output of L1 run. This typically has .nc extension
            l2_run_output (str): A file path for the output of L2 run. This typically has .nc extension
            l2_ameriflux_output (str): A file path for the generated L2.txt that is formatted for Ameriflux standards
            spaces (str): Spaces to be inserted before each section and line
            level_line (str): Line specifying the level. L2 for this section.
        Returns:
            None
        """
        # open input file in read mode
        l2_mainstem = open(l2_mainstem, 'r')
        l2_ameriflux = open(l2_ameriflux_only, 'r')
        l2_output_lines = []  # comma separated list of lines to be written
        # read lines from l1 inputs
        l2_mainstem_lines = l2_mainstem.readlines()
        l2_ameriflux_lines = l2_ameriflux.readlines()

        # writing to output file

        # write the level line
        l2_output_lines.append(level_line.strip())

        # write Files section
        files_lines = []
        files_lines.append("[Files]")
        filename = os.path.basename(l1_run_output)
        file_path = os.path.dirname(l1_run_output)
        out_filename = os.path.basename(l2_run_output)

        file_path_line = spaces + "file_path = " + file_path
        files_lines.append(file_path_line)
        in_filename_line = spaces + "in_filename = " + filename
        files_lines.append(in_filename_line)
        out_filename_line = spaces + "out_filename = " + out_filename
        files_lines.append(out_filename_line)
        # write lines to l1 output
        l2_output_lines.extend(files_lines)


        # get starting index for Variables section
        mainstem_variable_ind = L2Format.get_variable_line_index(l2_mainstem_lines)
        ameriflux_variable_ind = L2Format.get_variable_line_index(l2_ameriflux_lines)

        mainstem_lines_out, mainstem_plots_ind = L2Format.read_l2_lines(l2_mainstem_lines[mainstem_variable_ind+1:],
                                                                        pyfluxpro_ameriflux_labels)
        ameriflux_lines_out, ameriflux_plots_ind = L2Format.read_l2_lines(l2_ameriflux_lines[mainstem_variable_ind + 1:],
                                                                          pyfluxpro_ameriflux_labels)


    @staticmethod
    def get_variable_line_index(lines):
        """
            Get Variables section starting line index

            Args:
                lines (list): List of the strings that are read fom L1.txt
            Returns:
                ind (integer): Index of [Variables] section
        """
        for ind, line in enumerate(lines):
            if line.strip() == "[Variables]":
                return ind

    @staticmethod
    def read_l2_lines(lines, pyfluxpro_ameriflux_labels, pattern=VAR_PATTERN_WITH_SPACE):
        """
            Read L2 file lines and replace variable names according to labels key.
            Returns index where Variables section ends and the output lines

            Args:
                lines (list): List of the strings that are read fom L2.txt
                pyfluxpro_ameriflux_labels (dict): Mapping from pyfluxpro-friendly labels to ameriflux-friendly labels
                pattern (str): Regex pattern for a variable name line in L2.txt
            Returns:
                ind (integer): Ending index of [Variables] section or the starting index of [Plots] section
                output_lines (list): List of strings to be written to L2 output
        """
        output_lines = []  # list of strings to be written to file
        var_flag = False  # flag to see if variable is present in label keys
        for ind, line in enumerate(lines):
            line = line.rstrip("\n")
            if line.strip() == ['Plots']:
                return output_lines, ind
            matched = re.match(pattern, line)
            if matched:
                var_line = matched.group(0)
                var_name = var_line.strip().strip('[]')
                if var_name in pyfluxpro_ameriflux_labels.keys():
                    # replace the variable name
                    line.replace(var_name, pyfluxpro_ameriflux_labels[var_name])
                    output_lines.extend(line)
