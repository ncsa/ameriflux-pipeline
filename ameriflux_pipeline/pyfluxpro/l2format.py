# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import re
import logging

import utils.data_util as data_util
from utils.process_validation import DataValidation, L2Validation

# create log object with current module name
log = logging.getLogger(__name__)


class L2Format:
    """
    Class to implement formatting of PyFluxPro L2 control file as per AmeriFlux standards
    """
    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L2
    LEVEL_LINE = "level = L2"  # set the level
    VAR_PATTERN = '^\\[\\[[a-zA-Z0-9_]+\\]\\]$'  # variable name pattern
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'
    DEPENDENCYCHECK_PATTERN = '^\\[\\[\\[DependencyCheck\\]\\]\\]$'
    EXCLUDEDATES_PATTERN = '^\\[\\[\\[ExcludeDates\\]\\]\\]$'
    RANGECHECK_PATTERN = '^\\[\\[\\[RangeCheck\\]\\]\\]$'

    # main method which calls other functions
    @staticmethod
    def data_formatting(ameriflux_labels, l2_mainstem, l2_ameriflux_only, l1_run_output, l2_run_output,
                        l2_ameriflux_output, spaces=SPACES, level_line=LEVEL_LINE):
        """
        Main method for the class.

        Args:
            ameriflux_labels (dict): Mapping of variable names to Ameriflux-friendly labels read in l1
            l2_mainstem (str): A file path for the input L2.txt. This is the PyFluxPro original/mainstem L2 control file
            l2_ameriflux_only (str): A file path for the L2.txt that contains only Ameriflux-friendly variables
            l1_run_output (str): A file path for the output of L1 run. This typically has .nc extension
            l2_run_output (str): A file path for the output of L2 run. This typically has .nc extension
            l2_ameriflux_output (str): A file path for the generated L2.txt that is formatted for Ameriflux standards
            spaces (str): Spaces to be inserted before each section and line
            level_line (str): Line specifying the level. L2 for this section.
        Returns:
            (bool): True if success, False if not
        """
        # read lines from l1 inputs
        l2_mainstem_lines = data_util.read_file_lines(l2_mainstem)
        # check if input L1 have the same format as expected
        if (not l2_mainstem_lines) or (not L2Validation.check_l2_format(l2_mainstem_lines)):
            log.error("Check input L2.txt format %s", l2_mainstem)
            return False
        l2_ameriflux_lines = data_util.read_file_lines(l2_ameriflux_only)
        if (not l2_ameriflux_lines) or (not L2Validation.check_l2_format(l2_ameriflux_lines)):
            log.error("Check input L2.txt format %s", l2_ameriflux_only)
            return False

        l2_output_lines = []  # comma separated list of lines to be written

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
        mainstem_variable_startind = L2Format.get_variable_line_index(l2_mainstem_lines)
        ameriflux_variable_startind = L2Format.get_variable_line_index(l2_ameriflux_lines)

        # get index for Plots section
        mainstem_plot_ind = L2Format.get_plots_line_index(l2_mainstem_lines)
        ameriflux_plot_ind = L2Format.get_plots_line_index(l2_ameriflux_lines)

        if mainstem_plot_ind:
            mainstem_plot_startind = mainstem_plot_ind
            mainstem_plot_endind = len(l2_mainstem_lines)
            mainstem_variable_endind = mainstem_plot_ind - 1
        else:
            mainstem_plot_startind = None
            mainstem_plot_endind = None
            mainstem_variable_endind = len(l2_mainstem_lines)
        if ameriflux_plot_ind:
            ameriflux_plot_startind = ameriflux_plot_ind
            ameriflux_plot_endind = len(l2_ameriflux_lines)
            ameriflux_variable_endind = ameriflux_plot_ind - 1
        else:
            ameriflux_plot_startind = None
            ameriflux_plot_endind = None
            ameriflux_variable_endind = len(l2_ameriflux_lines)

        # get the variables section lines
        l2_mainstem_var_lines = l2_mainstem_lines[mainstem_variable_startind + 1: mainstem_variable_endind]
        l2_ameriflux_var_lines = l2_ameriflux_lines[ameriflux_variable_startind + 1: ameriflux_variable_endind]

        # write variable line
        variable_line = ["[Variables]"]
        l2_output_lines.extend(variable_line)

        # remove newline and extra spaces from each line
        mainstem_var_lines = [x.strip() for x in l2_mainstem_var_lines]
        ameriflux_var_lines = [x.strip() for x in l2_ameriflux_var_lines]

        # get list of variable start and end indexes
        mainstem_var_start_end, mainstem_var_names = L2Format.get_variables_index(mainstem_var_lines, [],
                                                                                  ameriflux_labels)
        ameriflux_var_start_end, all_var_names = L2Format.get_variables_index(ameriflux_var_lines, mainstem_var_names,
                                                                              ameriflux_labels)

        # get the variable lines to be written
        ameriflux_variable_lines_out, ameriflux_l2_var_name_out = \
            L2Format.format_variables(ameriflux_var_lines, ameriflux_var_start_end, ameriflux_labels, [])
        l2_output_lines.extend(ameriflux_variable_lines_out)
        mainstem_variable_lines_out, all_l2_var_name_out = \
            L2Format.format_variables(mainstem_var_lines, mainstem_var_start_end, ameriflux_labels,
                                      ameriflux_l2_var_name_out)
        l2_output_lines.extend(mainstem_variable_lines_out)

        # get the Plots section from Mainstem L2
        plot_line = ["[Plots]"]
        l2_output_lines.extend(plot_line)
        l2_mainstem_plot_lines = l2_mainstem_lines[mainstem_plot_startind:mainstem_plot_endind]
        l2_mainstem_plot_lines = [line.rstrip() for line in l2_mainstem_plot_lines]
        plot_lines_out = L2Format.format_plots(l2_mainstem_plot_lines, ameriflux_labels)
        l2_output_lines.extend(plot_lines_out)

        # write output lines to file
        log.info("Writting Ameriflux L2 control file to " + l2_ameriflux_output)
        data_util.write_list_to_file(l2_output_lines, l2_ameriflux_output)
        # process successfully completed
        return True

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
    def get_plots_line_index(lines):
        """
            Get Plots section starting line index

            Args:
                lines (list): List of the strings that are read fom L2.txt

            Returns:
                ind (integer): Index of [Plots] section
        """
        # read from the end as Plots section is the last section
        # if Plots section does not exist, return None
        for ind, line in enumerate(lines[::-1]):
            if line.strip() == "[Plots]":
                return len(lines) - ind
        return None

    @staticmethod
    def get_variables_index(text, current_var_names, labels, var_pattern=VAR_PATTERN):
        """
            Get all variables and start and end index for each variable from L2.txt
            Read variable lines and updated var_names list with read variables. Avoid duplicates.

            Args:
                text (list): list of strings with all variable lines from L1.txt
                current_var_names (list): list of variable names read till now. Used to check for duplicates
                labels (dict) : Mapping of variable names to ameriflux labels
                var_pattern (str): Regex pattern to find the starting line for [Variables] section
            Returns:
                var_start_end (list): List of tuples with variable name, start and end index for each variable
                var_names (list): list of variable names read till now
        """
        var_startind = []  # list of tuples with variable name, start index for each variable
        var_start_end = []  # list of tuples with variable name, start and end index for each variable
        for i, line in enumerate(text):
            if re.match(var_pattern, line):
                var_startind.append((line, i))
        # from var_startind, get starting and ending indexes
        for i in range(len(var_startind)-1):
            var_name = var_startind[i][0].strip('[]')
            if var_name in current_var_names:
                # var_name already written. Skip this variable
                log.warning("Variable " + var_name + " is already read in L2. Skipping this variable.")
                continue
            elif var_name not in labels.keys():
                # var_name not in L1 labels. Skip this variable
                log.warning("Variable " + var_name + " is not in L1. Skipping this variable.")
                continue
            # add starting and ending index only if not read previously
            start_ind = var_startind[i][1]
            # ending index is one less than the next starting index
            end_ind = var_startind[i + 1][1] - 1
            var_start_end.append((var_name, start_ind, end_ind))
            current_var_names.append(var_name)  # append pyfluxpro label
            current_var_names.append(labels[var_name])  # append ameriflux label
        # add last variable
        var_name = var_startind[-1][0].strip('[]')
        if var_name in current_var_names:
            # var_name already written. Skip this variable
            log.warning("Variable " + var_name + " is already read in L2. Skipping this variable.")
        elif var_name not in labels.keys():
            # var_name not in L1 labels. Skip this variable
            log.warning("Variable " + var_name + " is not in L1. Skipping this variable.")
        else:
            var_start_end.append((var_startind[-1][0], var_startind[-1][1], len(text)))
            current_var_names.append(var_name)  # append pyfluxpro label
            current_var_names.append(labels[var_name])  # append ameriflux label

        return var_start_end, current_var_names

    @staticmethod
    def format_variables(variable_lines, var_start_end, labels, l2_var_name_out, spaces=SPACES,
                         RangeCheck_pattern=RANGECHECK_PATTERN, DependencyCheck_pattern=DEPENDENCYCHECK_PATTERN):
        """
            Change variable names and units to AmeriFlux standard

            Args:
                variable_lines (list): List of variable lines from L2 input file
                var_start_end (list): List of tuple, the starting and ending index for each variable
                labels (dict) : Mapping from pyfluxpro to ameriflux labels
                l2_var_name_out (list): List of variable names written in l2_ameriflux output control file till now
                spaces (str): Spaces to be inserted before each section and line
                RangeCheck_pattern (str): Regex pattern to find the [[[RangeCheck]]] section within Variables section
                DependencyCheck_pattern (str): Regex pattern to find the [[[DependencyCheck]]] section within Variables
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l2_ameriflux
                l2_var_name_out (list): Updated list of l2 variable names written to l2_ameriflux control file
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        check_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces
        variables_lines_out = []  # variable lines to be written to l2_ameriflux
        # iterate through each variable
        for var, var_start, var_end in var_start_end:
            var_out = []  # initialize list to append current variable lines
            var_lines = variable_lines[var_start:var_end+1]
            # get variable name
            var_name = var_lines[0].strip('[]')
            # check if variable is already written to L2
            if var_name in l2_var_name_out:
                log.warning("Variable " + var_name + " is already written to L2. Skipping this variable.")
                continue

            if var_name not in labels.keys():
                # only write Ameriflux-friendly variables. NOTES 13
                continue

            ameriflux_var_name = labels[var_name]
            var_out.append(var_spaces + "[[" + ameriflux_var_name + "]]")
            # add variable names to var_name_out
            l2_var_name_out.append(ameriflux_var_name)
            l2_var_name_out.append(var_name)

            # get list of check, start and end indexes for this variable
            var_checks = L2Format.get_variable_check_indexes(var_lines)
            for check, check_start, check_end in var_checks:
                if bool(re.match(RangeCheck_pattern, check)):
                    # range check section found. format it
                    first_line = var_lines[check_start]
                    second_line = var_lines[check_end]
                    if first_line.split('=')[0].strip().lower() == 'lower':
                        lower_line = first_line
                        upper_line = second_line
                    else:
                        lower_line = second_line
                        upper_line = first_line
                    # NOTES 15. Convert lower and upper ranges to percentage
                    if ameriflux_var_name.startswith("SWC_"):
                        # fix lower range
                        lower_range_values = lower_line.split('=')[1].strip().split(',')
                        lower_range_values = [float(x) * 100 for x in lower_range_values]
                        lower_line = ",".join([str(i) for i in lower_range_values])
                        lower_line = 'lower = ' + lower_line
                        # fix upper range
                        upper_range_values = upper_line.split('=')[1].strip().split(',')
                        upper_range_values = [float(x) * 100 for x in upper_range_values]
                        upper_line = ",".join([str(i) for i in upper_range_values])
                        upper_line = 'upper = ' + upper_line
                    # write to output list with proper spaces
                    var_out.append(check_spaces + check)
                    var_out.append(other_spaces + lower_line)
                    var_out.append(other_spaces + upper_line)

                elif bool(re.match(DependencyCheck_pattern, check)):
                    # dependency check found. format it
                    source_line = var_lines[check_start]
                    # replace values with pattern x_[0-9] with empty string
                    updated_source_line = re.sub(r"x_[0-9]+", "", source_line)
                    # NOTES 14
                    # change H2O_IRGA_Vr to H2O_SIGMA
                    updated_source_line = re.sub(r"H2O_IRGA_Vr", "H2O_SIGMA", updated_source_line)
                    # check if the source line is valid / not empty
                    sources = updated_source_line.split('=')
                    if len(sources) == 2:
                        # remove unnecessary comma
                        updated_source_line = re.sub(r",", '', updated_source_line)
                        sources = updated_source_line.split('=')
                        if sources[1] in ['', ' ']:
                            # the source line is empty
                            updated_source_line = ''
                    # add updated lines with appropriate spaces
                    if len(updated_source_line) > 0:
                        var_out.append(check_spaces + check)
                        var_out.append(other_spaces + updated_source_line)

                else:
                    # other checks. format with correct spaces
                    var_out.append(check_spaces + check)
                    for i in range(check_start, check_end+1):
                        var_out.append(other_spaces + var_lines[i])
            # end of for loop for checks
            variables_lines_out.extend(var_out)
        # end of for loop for variables
        return variables_lines_out, l2_var_name_out

    @staticmethod
    def get_variable_check_indexes(var_lines):
        """
            Get the starting and ending indexes for each variable in the L2 input file
            Args:
                var_lines (list): List of variable lines from L2 input file
            Returns:
                var_start_end (list) : List of tuple, the starting and ending index for each variable
        """
        check_start_end = []
        # get the starting and ending indexes for each check
        for ind, line in enumerate(var_lines):
            if L2Format.is_check_line(line):
                # found a check, get start and end indexes
                start_ind = ind+1
                end_ind = ind+1
                while end_ind < len(var_lines) and not L2Format.is_check_line(var_lines[end_ind]):
                    end_ind += 1
                if start_ind == end_ind:
                    # empty check section. proceed with other checks without writing to l2_ameriflux
                    continue
                else:
                    check_start_end.append((line, start_ind, end_ind-1))
        return check_start_end

    @staticmethod
    def is_check_line(line):
        """
            Check if the line is a check line
            Args:
                line (str): A string of a line from L2 input file
            Returns:
                (bool) : True if the line is a check line, False otherwise
        """
        if line.startswith('[[[') and line.endswith(']]]'):
            return True
        else:
            return False

    @staticmethod
    def format_plots(plot_lines, labels, spaces=SPACES):
        """
            Format Plots section lines as per Ameriflux Standard. Replace variables with Ameriflux-friendly labels
            Args:
                plot_lines (list): List of the strings from l2 plot section
                labels (dict) : Mapping from pyfluxpro to ameriflux labels
                spaces (str): Spaces to be inserted before each section and line
            Returns:
                (list) : List of strings formatted for Ameriflux
        """
        plot_lines_out = ['' for _ in range(len(plot_lines))]  # create empty list of length same as plots section
        other_spaces = spaces + spaces  # spaces for Variables line

        for ind, line in enumerate(plot_lines):
            if str(line).strip().startswith('variables'):
                # get list of variable names and replace with Ameriflux-friendly labels
                variables = line.split('=')[1].strip()
                variables_list = variables.split(',')
                updated_variables_list = []
                for var in variables_list:
                    if var in labels:
                        updated_variables_list.append(labels[var])
                updated_variables = ','.join(updated_variables_list)
                plot_lines_out[ind] = other_spaces + 'variables = ' + updated_variables
            else:
                plot_lines_out[ind] = line

        return plot_lines_out
