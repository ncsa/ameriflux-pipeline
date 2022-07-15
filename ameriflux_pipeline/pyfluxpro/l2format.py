# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import os
import re
import logging

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
            (bool): True if success, False if not
        """
        # open input file in read mode
        l2_mainstem = open(l2_mainstem, 'r')
        l2_ameriflux = open(l2_ameriflux_only, 'r')
        l2_output_lines = []  # comma separated list of lines to be written
        # read lines from l1 inputs
        l2_mainstem_lines = l2_mainstem.readlines()
        l2_ameriflux_lines = l2_ameriflux.readlines()

        # check if input L1 have the same format as expected
        if not L2Validation.check_l2_format(l2_mainstem_lines) or not L2Validation.check_l2_format(l2_ameriflux_lines):
            log.error("Check L2.txt format")
            l2_mainstem.close()
            l2_ameriflux.close()
            return False

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

        # get index for Plots section
        l2_mainstem_lines_last_valid_index = len(l2_mainstem_lines) - 1
        mainstem_plot_ind = l2_mainstem_lines_last_valid_index - L2Format.get_plots_line_index(l2_mainstem_lines)
        l2_ameriflux_lines_last_valid_index = len(l2_ameriflux_lines) - 1
        ameriflux_plot_ind = l2_ameriflux_lines_last_valid_index - L2Format.get_plots_line_index(l2_ameriflux_lines)

        # get the variables section lines
        l2_mainstem_var_lines = l2_mainstem_lines[mainstem_variable_ind + 1: mainstem_plot_ind]
        l2_ameriflux_var_lines = l2_ameriflux_lines[ameriflux_variable_ind + 1: ameriflux_plot_ind]

        # write variable line
        variable_line = ["[Variables]"]
        l2_output_lines.extend(variable_line)

        # write the variables section to dataframe. this is used to get the indexes easily
        mainstem_var_df = pd.DataFrame(l2_mainstem_var_lines, columns=['Text'])
        # remove newline and extra spaces from each line
        mainstem_var_df['Text'] = mainstem_var_df['Text'].apply(lambda x: x.strip())
        ameriflux_var_df = pd.DataFrame(l2_ameriflux_var_lines, columns=['Text'])
        ameriflux_var_df['Text'] = ameriflux_var_df['Text'].apply(lambda x: x.strip())

        # get df with only variables and a list of variable start and end indexes
        ameriflux_variables, ameriflux_var_start_end = L2Format.get_variables_index(ameriflux_var_df['Text'])
        mainstem_variables, mainstem_var_start_end = L2Format.get_variables_index(mainstem_var_df['Text'])

        # get the variable lines to be written
        ameriflux_variable_lines_out = L2Format.format_variables(ameriflux_var_df, ameriflux_var_start_end,
                                                                 pyfluxpro_ameriflux_labels)
        l2_output_lines.extend(ameriflux_variable_lines_out)
        mainstem_variable_lines_out = L2Format.format_variables(mainstem_var_df, mainstem_var_start_end,
                                                                pyfluxpro_ameriflux_labels)
        l2_output_lines.extend(mainstem_variable_lines_out)

        # get the Plots section from Mainstem L2
        l2_mainstem_plot_lines = l2_mainstem_lines[mainstem_plot_ind:l2_mainstem_lines_last_valid_index + 1]
        l2_mainstem_plot_lines = [line.rstrip() for line in l2_mainstem_plot_lines]
        plot_lines_out = L2Format.format_plots(l2_mainstem_plot_lines, pyfluxpro_ameriflux_labels)
        l2_output_lines.extend(plot_lines_out)

        # write output lines to file
        L2Format.write_list_to_file(l2_output_lines, l2_ameriflux_output)
        # processing completed
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
        for ind, line in enumerate(lines[::-1]):
            if line.strip() == "[Plots]":
                return ind

    @staticmethod
    def get_variables_index(text, var_pattern=VAR_PATTERN):
        """
            Get all variables and start and end index for each variable from L1.txt

            Args:
                text (obj): Pandas series with all variable lines from L1.txt
                var_pattern (str): Regex pattern to find the starting line for [Variables] section
            Returns:
                variables (obj) : Pandas series. This is a subset of the input dataframe with only variable names
                var_start_end (list): List of tuple, the starting and ending index for each variable
        """
        variables = text[text.str.contains(var_pattern)]
        var_start_end = []
        for i in range(len(variables.index) - 1):
            start_ind = variables.index[i]
            end_ind = variables.index[i + 1]
            var_start_end.append((start_ind, end_ind))
        # append the start and end index of the last variable
        var_start_end.append((end_ind, text.last_valid_index()+1))
        return variables, var_start_end

    @staticmethod
    def format_variables(df, var_start_end, labels, spaces=SPACES, DependencyCheck_pattern=DEPENDENCYCHECK_PATTERN,
                         ExcludeDates_pattern=EXCLUDEDATES_PATTERN, RangeCheck_pattern=RANGECHECK_PATTERN):
        """
            Change variable names and units to AmeriFlux standard

            Args:
                df (obj): Pandas dataframe with all variable lines from L1_mainstem.txt
                var_start_end (list): List of tuple, the starting and ending index for each variable
                labels (dict) : Mapping from pyfluxpro to ameriflux labels
                spaces (str): Spaces to be inserted before each section and line
                DependencyCheck_pattern (str): Regex pattern to find the [[[DependencyCheck]]] section within Variables
                ExcludeDates_pattern (str): Regex pattern to find the [[[ExcludeDates]]] section within Variables
                RangeCheck_pattern (str): Regex pattern to find the [[[RangeCheck]]] section within Variables section
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l2_ameriflux
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        DependencyCheck_spaces = spaces + spaces
        ExcludeDates_spaces = spaces + spaces
        RangeCheck_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_lines_out = []  # variable lines to be written

        # iterate over the variables
        for start, end in var_start_end:
            indexes = {'ExcludeDates': None, 'DependencyCheck': None, 'RangeCheck': None}
            # get each variable in a separate df
            var = df[start:end]
            # change variable name according to ameriflux standards
            var_name = var['Text'].iloc[0].strip('[]')
            var_name_index = var.index[0]
            if var_name not in labels:
                # only write Ameriflux-friendly variables. NOTES 13
                continue
            ameriflux_var_name = labels[var_name]
            var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + ameriflux_var_name + "]]"

            # get the RangeCheck section
            RangeCheck = var[var['Text'].str.contains(RangeCheck_pattern)]
            if not RangeCheck.empty:
                indexes['RangeCheck'] = RangeCheck.index[0]

            # get the ExcludeDates section
            ExcludeDates = var[var['Text'].str.contains(ExcludeDates_pattern)]
            if not ExcludeDates.empty:
                indexes['ExcludeDates'] = ExcludeDates.index[0]

            # get the [[[DependencyCheck]]] section
            DependencyCheck = var[var['Text'].str.contains(DependencyCheck_pattern)]
            if not DependencyCheck.empty:
                indexes['DependencyCheck'] = DependencyCheck.index[0]

            # get indexes in sorted order - always 3
            sorted_indexes = dict(sorted(indexes.items(), key=lambda item: (item[1] is None, item[1])))
            sorted_indexes_keys = list(sorted_indexes.keys())
            sorted_indexes_values = list(sorted_indexes.values())
            section0_name = sorted_indexes_keys[0]
            section0_startindex = sorted_indexes_values[0]
            section1_name = sorted_indexes_keys[1]
            section1_startindex = sorted_indexes_values[1]
            section2_name = sorted_indexes_keys[2]
            section2_startindex = sorted_indexes_values[2]

            if section1_startindex is not None:
                section0_endindex = section1_startindex
            else:
                # index 1 value is None
                # if index 1 is None, index 2 is also None because of sorting
                # section ends where variable section ends
                section0_endindex = end

            first_df = var.loc[section0_startindex: section0_endindex - 1]
            second_df, third_df = None, None
            if section2_startindex is not None:
                section1_endindex = section2_startindex
            else:
                section1_endindex = end

            if section2_startindex is not None:
                section2_endindex = end

            if section1_startindex is not None:
                second_df = var.loc[section1_startindex: section1_endindex - 1]
            if section2_startindex is not None:
                third_df = var.loc[section2_startindex: section2_endindex - 1]

            df_list = [first_df, second_df, third_df]  # contains the actual df
            df_list = [x for x in df_list if x is not None]

            # get the keys of sorted indexes
            title_list = [sorted_indexes_keys[0], sorted_indexes_keys[1], sorted_indexes_keys[2]]

            # initialize all sections as None
            DependencyCheck_df, RangeCheck_df, ExcludeDates_df = None, None, None

            range_index = title_list.index("RangeCheck")
            if range_index < len(df_list):
                RangeCheck_df = df_list[range_index]
                # format with spaces
                first_index = RangeCheck_df.first_valid_index()
                if first_index:
                    if ameriflux_var_name.startswith("SWC_"):
                        # NOTES 15. Convert lower and upper ranges to percentage
                        first_line = RangeCheck_df['Text'].loc[first_index + 1]
                        second_line = RangeCheck_df['Text'].loc[first_index + 2]
                        if first_line.split('=')[0].strip() == 'lower':
                            lower_line = first_line
                            upper_line = second_line
                        else:
                            lower_line = second_line
                            upper_line = first_line
                        # fix lower range
                        lower_range_values = lower_line.split('=')[1].strip().split(',')
                        lower_range_values = [float(x) * 100 for x in lower_range_values]
                        lower_line = ",".join([str(i) for i in lower_range_values])
                        lower_line = 'lower = ' + lower_line
                        RangeCheck_df['Text'].loc[first_index + 1] = lower_line
                        # fix upper range
                        upper_range_values = upper_line.split('=')[1].strip().split(',')
                        upper_range_values = [float(x) * 100 for x in upper_range_values]
                        upper_line = ",".join([str(i) for i in upper_range_values])
                        upper_line = 'upper = ' + upper_line
                        RangeCheck_df['Text'].loc[first_index + 2] = upper_line

                    # set the correct spaces
                    RangeCheck_df['Text'].loc[first_index] = \
                        RangeCheck_spaces + RangeCheck_df['Text'].loc[first_index]
                    RangeCheck_df['Text'].loc[first_index + 1:] = \
                        other_spaces + RangeCheck_df['Text'].loc[first_index + 1:]
                    # update var df
                    var.update(RangeCheck_df)

            ex_index = title_list.index("ExcludeDates")
            if ex_index < len(df_list):
                ExcludeDates_df = df_list[ex_index]
                # format with spaces
                first_index = ExcludeDates_df.first_valid_index()
                if first_index:
                    ExcludeDates_df['Text'].loc[first_index] = \
                        ExcludeDates_spaces + ExcludeDates_df['Text'].loc[first_index]
                    ExcludeDates_df['Text'].loc[first_index + 1:] = \
                        other_spaces + ExcludeDates_df['Text'].loc[first_index + 1:]
                    var.update(ExcludeDates_df)

            # Dependency check is done at last since we might need to delete the whole check itself.
            # dropping rows is easier to be done at the end
            dep_index = title_list.index("DependencyCheck")
            if dep_index < len(df_list):
                DependencyCheck_df = df_list[dep_index]
                # get the source line and delete footprint variable with pattern x_[0-9]+
                source_line = DependencyCheck_df['Text'].iloc[1]  # source line is the second line of df
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
                first_index = DependencyCheck_df.first_valid_index()
                if first_index and len(updated_source_line) > 0:
                    # update only if valid index and valid source line
                    DependencyCheck_df['Text'].loc[first_index] = DependencyCheck_spaces + \
                                                                  DependencyCheck_df['Text'].loc[first_index]
                    DependencyCheck_df['Text'].loc[first_index + 1] = other_spaces + updated_source_line
                    var.update(DependencyCheck_df)
                elif first_index:
                    # delete DependencyCheck df from var
                    var.drop([first_index, first_index+1], inplace=True)

            variables_lines_out.extend(var['Text'].tolist())

        return variables_lines_out

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
        plot_lines_out = ['' for i in range(len(plot_lines))]  # create empty list of length same as plots section
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

    @staticmethod
    def write_list_to_file(in_list, outfile):
        """
            Save list with string to a file
            Args:
                in_list (list): List of the strings
                outfile (str): A file path of the output file
            Returns:
                None
        """
        try:
            with open(outfile, 'w') as f:
                f.write('\n'.join(in_list))
            log.info("AmeriFlux L2 saved in %s", outfile)
        except Exception as e:
            log.error("Failed to create file %s. %s", outfile, e)
