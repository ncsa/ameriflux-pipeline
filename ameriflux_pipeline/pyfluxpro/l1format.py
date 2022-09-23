# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd
import os
import re
import logging

import utils.data_util as data_util
from utils.process_validation import DataValidation, L1Validation

# create log object with current module name
log = logging.getLogger(__name__)


class L1Format:
    """
    Class to implement formatting of PyFluxPro L1 control file as per AmeriFlux standards
    """
    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L1
    LEVEL_LINE = "level = L1"  # set the level

    # define patterns to match
    # variable names have alphanumeric characters and underscores with two square brackets
    VAR_PATTERN = '^\\[\\[[a-zA-Z0-9_]+\\]\\]$'
    # variable name lines starts with 4 spaces followed by
    # characters and/or digits within two square brackets and ends with new line
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'
    XL_PATTERN = '^\\[\\[\\[xl\\]\\]\\]$'  # to match [[[xl]]] line
    ATTR_PATTERN = '^\\[\\[\\[Attr\\]\\]\\]$|^\\[\\[\\[attr\\]\\]\\]$'  # to match [[Attr]] or [[attr]] line
    UNITS_PATTERN = 'units'
    LONG_NAME_PATTERN = 'long_name'
    NAME_PATTERN = 'name'
    SHEET_PATTERN = 'sheet'
    # set site name regex pattern.
    # Starts with site_name followed by optional space and then equal sign followed by
    # a word with min of 3 and max of 50 characters
    SITE_NAME_LINE_PATTERN = "^site_?name\s?=\s?[\w\W]{3,50}$"

    # main method which calls other functions
    @staticmethod
    def data_formatting(pyfluxpro_input, l1_mainstem, l1_ameriflux_only, ameriflux_mainstem_key, file_meta_data_file,
                        outfile, l1_ameriflux_output, erroring_variable_flag, erroring_variable_key,
                        site_soil_moisture_variables, site_soil_temp_variables,
                        full_output_variables, met_data_variables,
                        spaces=SPACES, level_line=LEVEL_LINE):
        """
        Main method for the class.

        Args:
            pyfluxpro_input (str): A file path for the PyFluxPro input excel sheet formatted for Ameriflux
            l1_mainstem (str): A file path for the input L1.txt. This is the PyFluxPro original/mainstem L1 control file
            l1_ameriflux_only (str): A file path for the L1.txt that contains only Ameriflux-friendly variables
            ameriflux_mainstem_key (str): Variable name key used to match the original variable names to Ameriflux names
                                            This is an excel file named Ameriflux-Mainstem-Key.xlsx
            file_meta_data_file (str) : CSV file containing the meta data, typically the first line of Met data
            outfile (str): A file path for the output of L1 run. This typically has .nc extension
            l1_ameriflux_output (str): A file path for the L1.txt that is formatted for Ameriflux standards
            erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) are
                                        renamed to Ameriflux labels in L1. Y is renamed, N if not. By default it is N.
            erroring_variable_key (str): Variable name key used to match the original variable names to Ameriflux names
                                        for variables throwing an error in PyFluxPro L1.
                                        This is an excel file named L1_erroring_variables.xlsx
            site_soil_moisture_variables (dict): Dictionary for soil moisture variable details from Soils key file
            site_soil_temp_variables (dict): Dictionary for soil temperature variable details from Soils key file
            full_output_variables (list): List of full_output variable names
            met_data_variables (list): List of met_data variable names
            spaces (str): Spaces to be inserted before each section and line
            level_line (str): Line specifying the level. L1 for this section.
        Returns:
            ameriflux_mapping (dict): Mapping of variable names to Ameriflux-friendly labels
                                        for variables in L1_Ameriflux.txt
        """
        # read lines from l1 inputs
        l1_mainstem_lines = data_util.read_file_lines(l1_mainstem)
        # check if input L1 have the same format as expected
        if (not l1_mainstem_lines) or (not L1Validation.check_l1_format(l1_mainstem_lines)):
            log.error("Check input L1.txt format %s", l1_mainstem)
            return None
        l1_ameriflux_lines = data_util.read_file_lines(l1_ameriflux_only)
        if (not l1_ameriflux_lines) or (not L1Validation.check_l1_format(l1_ameriflux_lines)):
            log.error("Check input L1.txt format %s", l1_ameriflux_only)
            return None

        l1_output_lines = []  # comma separated list of lines to be written

        # read file_meta
        file_meta = data_util.read_csv_file(file_meta_data_file)
        # get the site name
        file_site_name = file_meta.iloc[0][5]
        site_name = data_util.get_site_name(file_site_name)

        # get AmeriFlux-Mainstem variable name matching key
        ameriflux_key = L1Format.get_ameriflux_key(ameriflux_mainstem_key)
        if ameriflux_key.empty:
            return None

        if erroring_variable_flag.lower() in ['n', 'no']:
            # if user chose not to replace the variable name, read the name mapping
            # if this file is read, the instance becomes a dataframe, if not the variable type is a string
            erroring_variable_key = pd.read_excel(erroring_variable_key)  # read L1 erroring variable name matching file
            if DataValidation.is_valid_erroring_variables_key(erroring_variable_key):
                # strip column names of extra spaces and convert to lowercase
                erroring_variable_key.columns = erroring_variable_key.columns.str.strip().str.lower()
                ameriflux_col = erroring_variable_key.filter(regex="ameriflux").columns.to_list()
                pyfluxpro_col = erroring_variable_key.filter(regex="pyfluxpro").columns.to_list()
                erroring_variable_key['Ameriflux label'] = erroring_variable_key[ameriflux_col]
                erroring_variable_key['PyFluxPro label'] = erroring_variable_key[pyfluxpro_col]
            else:
                log.warning("L1 Erroring Variables.xlsx file invalid format. Proceeding without replacing label")
                # make erroring_variable_key a string to proceed with pipeline.
                erroring_variable_key = ''

        # writing to output file

        # write the level line
        l1_output_lines.append(level_line.strip())

        # write Files section
        files_lines = []
        files_lines.append("[Files]")
        filename = os.path.basename(pyfluxpro_input)
        file_path = os.path.dirname(pyfluxpro_input)
        out_filename = os.path.basename(outfile)

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
        mainstem_global_lines, mainstem_variable_ind = L1Format.get_global_lines(l1_mainstem_lines, site_name)
        ameriflux_global_lines, ameriflux_variable_ind = L1Format.get_global_lines(l1_ameriflux_lines, site_name)
        # write global section lines to l1 output
        l1_output_lines.extend(mainstem_global_lines)

        # write variable line
        variable_line = ["[Variables]"]
        l1_output_lines.extend(variable_line)

        # write the variables section to dataframe. this is used to get the indexes easily
        mainstem_var_df = pd.DataFrame(l1_mainstem_lines[mainstem_variable_ind + 1:], columns=['Text'])
        # remove newline and extra spaces from each line
        mainstem_var_df['Text'] = mainstem_var_df['Text'].apply(lambda x: x.strip())
        # get df with only variables and a list of variable start and end indexes
        mainstem_variables, mainstem_var_start_end = L1Format.get_variables_index(mainstem_var_df['Text'])
        # get the mainstem variable lines to be written and variable name mapping
        mainstem_var_lines_out, mainstem_variable_ameriflux_mapping = \
            L1Format.format_mainstem_var(mainstem_var_df, mainstem_var_start_end,
                                         ameriflux_key, erroring_variable_key,
                                         site_soil_moisture_variables, site_soil_temp_variables,
                                         full_output_variables, met_data_variables)

        # write variables section lines to l1 output
        l1_output_lines.extend(mainstem_var_lines_out)

        # read from Ameriflux only L1 file
        ameriflux_var_df = pd.DataFrame(l1_ameriflux_lines[ameriflux_variable_ind + 1:], columns=['Text'])
        # remove newline and extra spaces from each line
        ameriflux_var_df['Text'] = ameriflux_var_df['Text'].apply(lambda x: x.strip())
        # get df with only variables and a list of variable start and end indexes
        ameriflux_variables, ameriflux_var_start_end = L1Format.get_variables_index(ameriflux_var_df['Text'])
        # get the variable lines to be written
        ameriflux_var_lines_out, ameriflux_variable_ameriflux_mapping = \
            L1Format.format_ameriflux_var(ameriflux_var_df, ameriflux_var_start_end, ameriflux_key,
                                          full_output_variables, met_data_variables,
                                          mainstem_variable_ameriflux_mapping)

        # write variables section lines to l1 output
        l1_output_lines.extend(ameriflux_var_lines_out)

        # create dictionary mapping of variables . variable names : ameriflux labels
        ameriflux_mapping = mainstem_variable_ameriflux_mapping.copy()
        ameriflux_mapping.update(ameriflux_variable_ameriflux_mapping)

        # write output lines to file
        log.info("Writting Ameriflux L1 control file to " + l1_ameriflux_output)
        data_util.write_list_to_file(l1_output_lines, l1_ameriflux_output)

        # return pyfluxpro to ameriflux label mapping
        return ameriflux_mapping

    @staticmethod
    def get_ameriflux_key(ameriflux_mainstem_key):
        """
        Method to get ameriflux key dataframe
        Args :
            ameriflux_mainstem_key (str): path to ameriflux key file
        Returns :
            df_ameriflux_key (obj): ameriflux key dataframe
        """
        # read AmeriFlux-Mainstem variable name matching file
        df_ameriflux_key = data_util.read_excel(ameriflux_mainstem_key)
        if not DataValidation.is_valid_ameriflux_mainstem_key(df_ameriflux_key):
            log.error("Ameriflux-Mainstem-Key.xlsx file invalid format.")
            return None
        # get column names matching Ameriflux
        ameriflux_cols = df_ameriflux_key.filter(regex=re.compile("^ameriflux", re.IGNORECASE)).columns.to_list()
        # get column names matching Original
        original_cols = df_ameriflux_key.filter(regex=re.compile("^original", re.IGNORECASE)).columns.to_list()
        # get column names matching Input sheet or Met tower
        input_cols = df_ameriflux_key.filter(regex=re.compile("^input|^met", re.IGNORECASE)).columns.to_list()
        # get units column
        units_col = df_ameriflux_key.filter(regex=re.compile("^units", re.IGNORECASE)).columns.to_list()
        # rename columns
        df_ameriflux_key.rename(columns={ameriflux_cols[0]: 'Ameriflux variable name',
                                         original_cols[0]: 'Original variable name',
                                         input_cols[0]: 'Input sheet variable name',
                                         units_col[0]: 'Units after formatting'}, inplace=True)

        return df_ameriflux_key

    @staticmethod
    def get_global_lines(lines, site_name, site_name_line_pattern=SITE_NAME_LINE_PATTERN, spaces=SPACES):
        """
            Get Global section from L1.txt

            Args:
                lines (list): List of the strings that are read fom L1.txt
                site_name (str): Name of site read from met data
                site_name_line_pattern (str): Regex pattern to match site name line
                spaces (str): Spaces to be inserted before each section and line

            Returns:
                global_lines (list): List of strings to be written to l1_output
                ind (integer): Index of [Variables] section
        """
        global_lines = []
        global_start_writing = False  # flag to check if Global section is over
        for ind, line in enumerate(lines):
            if line.strip() == "[Global]":
                global_lines.append(line.strip())
                global_start_writing = True
                continue
            if global_start_writing:
                site_line_matched = re.match(site_name_line_pattern, line.strip().lower())
                if bool(site_line_matched):
                    site_name_parameter = line.strip().split('=')[0]  # get the portion with site name
                    site_name_line = site_name_parameter + ' = ' + site_name
                    global_lines.append(spaces + site_name_line)
                elif line.strip() == "[Variables]":
                    global_start_writing = False
                    return global_lines, ind
                else:
                    # write line
                    global_lines.append(spaces + line.strip())

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
    def get_ameriflux_variables(lines, pattern=VAR_PATTERN_WITH_SPACE):
        """
            Get list of variable names from l1_ameriflux_lines

            Args:
                lines (list): List of the strings that are read fom L1_ameriflux.txt
                pattern (str): Regex pattern for variable names including whitespaces
            Returns:
                ameriflux_var_list (list): List of variable names
        """
        r = re.compile(pattern)
        ameriflux_var_list = list(filter(r.match, lines))
        # strip spaces and brackets to get only the variable name
        ameriflux_var_list = [x.strip().strip('[]') for x in ameriflux_var_list]
        return ameriflux_var_list

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
        end_ind = text.first_valid_index()  # initialize end index
        for i in range(len(variables.index) - 1):
            start_ind = variables.index[i]
            end_ind = variables.index[i + 1]
            var_start_end.append((start_ind, end_ind))
        # append the start and end index of the last variable
        var_start_end.append((end_ind, text.last_valid_index()+1))
        return variables, var_start_end

    @staticmethod
    def get_var_xl_attr_df(df, start, end, xl_pattern=XL_PATTERN, attr_pattern=ATTR_PATTERN):
        """
            Get xl and attr sections from variable dataframe
            Args:
                df (obj): Pandas dataframe with all variable lines from L1.txt
                start (int): Starting index of the variable section
                end (int): Ending index of the variable section
                xl_pattern (str): Regex pattern to find the [[[xl]]] section within Variables section
                attr_pattern (str): Regex pattern to find the [[[Attr]]] section within Variables section
            Returns:
                var (obj) : Pandas dataframe with the specific variable section
                xl_df (obj): Pandas dataframe with xl section for the variable
                attr_df (obj): Pandas dataframe with attr section for the variable
        """
        # get variable in a dataframe
        var = df[start:end]
        # get the [[[xl]]] section
        xl = var[var['Text'].str.contains(xl_pattern)]
        # get the [[[Attr]]] OR [[[attr]]] section
        attr = var[var['Text'].str.contains(attr_pattern)]

        # check which section comes first
        if xl.index[0] > attr.index[0]:
            # attr section comes first
            xl_df = df[xl.index[0]:end]
            attr_df = df[attr.index[0]:xl.index[0]]
        else:
            # xl section comes first
            attr_df = df[attr.index[0]:end]
            xl_df = df[xl.index[0]:attr.index[0]]

        return var, xl_df, attr_df

    @staticmethod
    def check_variable_exists(var_name, variable_list):
        """
        Check if input variable exists in list
        Args:
            var_name (str): Variable name to be checked
            variable_list (list): List of variable names
        Returns:
            (bool): True if variable name in list
        """
        return var_name in variable_list

    @staticmethod
    def get_corrected_met_tower_var_name(met_tower_var_name):
        """
            Get corrected met tower variable name. See NOTES#20 for details.
            Some met tower variable names are changed in met merger. Get corrected name.
            Args:
                met_tower_var_name (str): Met tower variable name
            Returns:
                corrected_met_tower_var_name (str): Corrected met tower variable name
        """
        corrected_met_tower_var_name = met_tower_var_name  # set initial value as same
        # if VWC change to VWC1
        if bool(re.match('^VWC_', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'VWC1_' + met_tower_var_name.split('_')[1] + '_Avg'
        # if TC change to TC1
        elif bool(re.match('^TC_', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'TC1_' + met_tower_var_name.split('_')[1] + '_Avg'

        # if CM3Dn and Solar_Wm2 columns, rename to SWDn
        elif bool(re.match('^CM[1-9]Up', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'SWDn_Avg'
        elif bool(re.match('^Solar_Wm[1-9]', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'SWDn_Avg'
        # if CM3Dn and Sw_Out columns, rename to SWUp
        elif bool(re.match('^CM[1-9]Dn', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'SWUp_Avg'
        elif bool(re.match('^Sw_Out', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'SWUp_Avg'

        # if CG3Dn and CG3Up columns, rename to LWDn and LWUp
        elif bool(re.match('^CG[1-9]UpCo', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'LWDnCo_Avg'
        elif bool(re.match('^CG[1-9]DnCo', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'LWUpCo_Avg'
        # search for string ending with CG3Up or starting with CG3Up_Avg
        elif bool(re.match('CG[1-9]Up$|^CG[1-9]Up_Avg', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'LWDn_Avg'
        elif bool(re.match('CG[1-9]Dn$|^CG[1-9]Dn_Avg', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'LWUp_Avg'

        # NetTot or Net_Rad column is renamed to Rn_Avg
        elif bool(re.match('^NetTot', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'Rn_Avg'
        elif bool(re.match('^Net_?Rad', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'Rn_Avg'

        elif bool(re.match('^CNR[1-9]_?T_?C', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'CNRTC_Avg'
        elif bool(re.match('^CNR[1-9]_?T_?K', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'CNRTK_Avg'
        elif bool(re.match('^Rs_net', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'NetRs_Avg'
        elif bool(re.match('^Rl_net', met_tower_var_name, re.I)):
            corrected_met_tower_var_name = 'NetRl_Avg'

        return corrected_met_tower_var_name

    @staticmethod
    def get_corrected_height(height):
        """
        Convert height from cm to m.
            Args:
                height (str): Height from Soils Key
            Returns:
                height (str): Corrected height of variable
        """
        # convert cm to m
        # limit height to two decimal place and convert to string
        return str(round(int(height) / 100, 2))

    @staticmethod
    def format_mainstem_var(df, var_start_end, ameriflux_key, erroring_variable_key,
                            site_soil_moisture_variables, site_soil_temp_variables,
                            full_output_variables, met_data_variables,
                            spaces=SPACES):
        """
            Change variable names and units to AmeriFlux standard

            Args:
                df (obj): Pandas dataframe with all variable lines from L1_mainstem.txt
                var_start_end (list): List of tuple, the starting and ending index for each variable
                ameriflux_key (obj): Pandas dataframe of AmeriFlux-Mainstem varible name sheet
                erroring_variable_key (str/obj): Variable name key used to match the original variable names to
                                        Ameriflux names for variables throwing an error in PyFluxPro L1.
                site_soil_moisture_variables (dict): Dictionary for soil moisture variable details from Soils key file
                site_soil_temp_variables (dict): Dictionary for soil temperature variable details from Soils key file
                full_output_variables (list): List of full_output variable names
                met_data_variables (list): List of met_data variable names
                spaces (str): Spaces to be inserted before each section and line
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l1_ameriflux
                variables_mapping (dict) : Mapping of variable to ameriflux-friendly variable names in L1
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_lines_out = []  # variable lines to be written
        # mapping for variables to be written
        variable_ameriflux_mapping = {}  # dictionary of mapping variable names to ameriflux-friendly names
        # get xl and attr sections for soil moisture and temperature variables
        moisture_xl_df, moisture_attr_df, temp_xl_df, temp_attr_df = None, None, None, None
        # iterate over the variables
        for start, end in var_start_end:
            # NOTES 13
            var_flag = False  # flag to see if variable is to be written or not
            # get variable, xl and attr sections as separate dataframes
            var, xl_df, attr_df = L1Format.get_var_xl_attr_df(df, start, end)
            var_name = var['Text'].iloc[0].strip('[]')  # get variable name
            # check if variable is already written to L1
            if (var_name in variable_ameriflux_mapping.keys()) or (var_name in variable_ameriflux_mapping.values()):
                log.warning("Variable " + var_name + " is already written to L1. Skipping this variable.")
                continue
            var_name_index = var.index[0]  # get index of variable name
            # get met tower variable name
            xl_name_row = xl_df[xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
            xl_var_name = xl_name_row['Text'].iloc[0].split('=')[1].strip()
            # get the corrected met tower variable name
            met_tower_var_name = L1Format.get_corrected_met_tower_var_name(xl_var_name)
            # get which sheet
            sheet_row = xl_df[xl_df['Text'].apply(lambda x: x.strip().startswith("sheet"))]
            sheet_name = sheet_row['Text'].iloc[0].split('=')[1].strip()

            # check if variable present in specified sheet
            if sheet_name.lower().startswith("full"):
                found_full_output = L1Format.check_variable_exists(met_tower_var_name, full_output_variables)
                if not found_full_output:
                    log.warning("Variable %s not found in full_output sheet. Skipping variable", met_tower_var_name)
                    continue
            elif sheet_name.lower().startswith("met"):
                found_met_data = L1Format.check_variable_exists(met_tower_var_name, met_data_variables)
                if not found_met_data:
                    log.warning("Variable %s not found in met_data sheet. Skipping variable", met_tower_var_name)
                    continue

            units_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("unit"))]
            height_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("height"))]
            instrument_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("instrument"))]

            # format text as per L1
            xl_name_row_index = xl_name_row.index[0]
            xl_df['Text'].iloc[xl_df.index == xl_name_row_index] = "name = " + met_tower_var_name
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

            # update the variable df
            var.update(xl_df)
            var.update(attr_df)

            # check if the variable is one of the erroring variables in L1 PyFluxPro
            # check if the erroring_variable_key is a dataframe.
            if isinstance(erroring_variable_key, pd.DataFrame) and \
                    erroring_variable_key['PyFluxPro label'].isin([var_name]).any():
                # the variable name is one of the erroring variables.
                # do not replace the variable name with ameriflux label
                var_flag = True
                # add to the mapping
                variable_ameriflux_mapping[var_name] = var_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_name + "]]"

            # if the erroring variable is to be replaced, the Ameriflux friendly variable name is in ameriflux_key
            elif ameriflux_key['Input sheet variable name'].isin([met_tower_var_name]).any():
                var_flag = True
                # check if var name should be changed for Ameriflux
                var_ameriflux_name = ameriflux_key.loc[ameriflux_key['Input sheet variable name'] == met_tower_var_name,
                                                       'Ameriflux variable name'].iloc[0]
                # add to the mapping, both met tower and original pyfluxpro names
                variable_ameriflux_mapping[var_name] = var_ameriflux_name
                variable_ameriflux_mapping[met_tower_var_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"

                if units_row.shape[0] > 0:
                    # check if units need to be changed
                    var_units_index = units_row.index[0]
                    var_ameriflux_units = \
                        ameriflux_key.loc[ameriflux_key['Input sheet variable name'] == met_tower_var_name,
                                          'Units after formatting'].iloc[0]
                    if not pd.isnull(var_ameriflux_units):
                        # if unit needs to be changed, if its not NaN in the ameriflux-mainstem sheet
                        # replace units only if it is not empty
                        var['Text'].iloc[var.index == var_units_index] = other_spaces + \
                                                                         "units = " + var_ameriflux_units
            # check if variable is soil moisture
            elif var_name.lower().startswith("sws_"):
                # soil moisture variable varies with site
                # save moisture variable xl and attr sections
                moisture_xl_df = xl_df
                moisture_attr_df = attr_df
                # format moisture variable lines
                # get the ameriflux variable name from site_soil_moisture_variables. continue if not found
                if met_tower_var_name not in site_soil_moisture_variables:
                    # met variables not found in site_soil_moisture_variables
                    continue
                var_ameriflux_name = site_soil_moisture_variables[met_tower_var_name]['Eddypro label']
                var_pyfluxpro_name = site_soil_moisture_variables[met_tower_var_name]['Pyfluxpro label']
                # write to variable lines
                var_flag = True
                # add met tower name to the mapping
                variable_ameriflux_mapping[met_tower_var_name] = var_ameriflux_name
                # add pyfluxpro name to the mapping
                variable_ameriflux_mapping[var_pyfluxpro_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"
                # change the unit to percentage
                if units_row.shape[0] > 0:
                    var_units_index = units_row.index[0]
                    var['Text'].iloc[var.index == var_units_index] = other_spaces + "units = " + '%'

                # correct the height row
                var_height_index = height_row.index[0]
                # get height from met variable name
                height_cm = site_soil_moisture_variables[met_tower_var_name]['Depth (cm)']
                height = L1Format.get_corrected_height(height_cm)
                var['Text'].iloc[var.index == var_height_index] = \
                    other_spaces + "height = " + '-' + height + 'm'

                # change the instrument row
                var_instrument_index = instrument_row.index[0]
                instrument = site_soil_moisture_variables[met_tower_var_name]['Instrument']
                if var_instrument_index is not None:
                    var['Text'].iloc[var.index == var_instrument_index] = \
                        other_spaces + "instrument = " + instrument
                # delete key from labels
                del site_soil_moisture_variables[met_tower_var_name]

            # check if variable is soil temp
            elif var_name.lower().startswith("ts_"):
                # soil temp variable varies with site
                # save temp variable xl and attr sections
                temp_xl_df = xl_df
                temp_attr_df = attr_df
                # format temp variable lines
                var_name_index = var.index[0]
                if met_tower_var_name not in site_soil_temp_variables:
                    # met variables not found in site_soil_temp_variables. skip writing to variable lines
                    continue
                var_ameriflux_name = site_soil_temp_variables[met_tower_var_name]['Eddypro label']
                var_pyfluxpro_name = site_soil_temp_variables[met_tower_var_name]['Pyfluxpro label']
                # write to variable lines
                var_flag = True
                # add met tower name to the mapping
                variable_ameriflux_mapping[met_tower_var_name] = var_ameriflux_name
                # add pyfluxpro name to the mapping
                variable_ameriflux_mapping[var_pyfluxpro_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"

                # correct the height row
                var_height_index = height_row.index[0]
                # get height from met variable name
                height_cm = site_soil_temp_variables[met_tower_var_name]['Depth (cm)']
                height = L1Format.get_corrected_height(height_cm)
                var['Text'].iloc[var.index == var_height_index] = \
                    other_spaces + "height = " + '-' + height + 'm'

                # change the instrument row
                var_instrument_index = instrument_row.index[0]
                instrument = site_soil_temp_variables[met_tower_var_name]['Instrument']
                if var_instrument_index is not None:
                    var['Text'].iloc[var.index == var_instrument_index] = \
                        other_spaces + "instrument = " + instrument
                # delete key from labels
                del site_soil_temp_variables[met_tower_var_name]

            if var_flag:
                # write the modified variable to the output list
                variables_lines_out.extend(var['Text'].tolist())
        # end of for loop. Variables in input L1 sheet are now formatted

        # if there are variables left in the labels, write them to the variables sheet
        if len(site_soil_moisture_variables) > 0 and moisture_attr_df is not None and moisture_xl_df is not None:
            # write moisture variables by modifying the attr and xl sections
            log.info("Writing additional soil moisture variables to L1 Variables")
            for key, value in site_soil_moisture_variables.items():
                # write if met variable in met_data sheet
                if L1Format.check_variable_exists(key, met_data_variables):
                    var_name_line = var_spaces + "[[" + value['Eddypro label'] + "]]"
                    variables_lines_out.append(var_name_line)
                    variable_ameriflux_mapping[key] = value['Eddypro label']  # add variable name to the mapping
                    name_row = moisture_xl_df[moisture_xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
                    moisture_xl_df.iloc[moisture_xl_df.index == name_row.index[0]] = other_spaces + "name = " + key
                    height_row = moisture_attr_df[moisture_attr_df['Text'].apply(lambda x:
                                                                                 x.strip().startswith("height"))]
                    # get height from met variable name
                    height_cm = value['Depth (cm)']
                    height = L1Format.get_corrected_height(height_cm)
                    moisture_attr_df.iloc[moisture_attr_df.index == height_row.index[0]] = \
                        other_spaces + "height = " + '-' + height + 'm'
                    # change instrument according to the met tower variable name
                    instrument_row = moisture_attr_df[moisture_attr_df['Text'].apply(
                        lambda x: x.strip().startswith("instrument"))]
                    instrument = value['Instrument']
                    moisture_attr_df.iloc[moisture_attr_df.index == instrument_row.index[0]] = \
                        other_spaces + "instrument = " + instrument
                    # write the modified sections
                    variables_lines_out.extend(moisture_attr_df['Text'].tolist())
                    variables_lines_out.extend(moisture_xl_df['Text'].tolist())
                else:
                    log.warning("Variable %s not found in met_data sheet. Skipping variable", key)

        if len(site_soil_temp_variables) > 0 and temp_attr_df is not None and temp_xl_df is not None:
            log.info("Writing additional soil temperature variables to L1 Variables")
            # write temp variables by modifying the attr and xl sections
            for key, value in site_soil_temp_variables.items():
                # write if met variable in met_data sheet
                if L1Format.check_variable_exists(key, met_data_variables):
                    var_name_line = var_spaces + "[[" + value['Eddypro label'] + "]]"
                    variables_lines_out.append(var_name_line)
                    variable_ameriflux_mapping[key] = value['Eddypro label']  # add variable name to the mapping
                    name_row = temp_xl_df[temp_xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
                    temp_xl_df.iloc[temp_xl_df.index == name_row.index[0]] = other_spaces + "name = " + key
                    height_row = temp_attr_df[temp_attr_df['Text'].apply(lambda x: x.strip().startswith("height"))]
                    # get height from met variable name
                    height_cm = value['Depth (cm)']
                    height = L1Format.get_corrected_height(height_cm)
                    temp_attr_df.iloc[temp_attr_df.index == height_row.index[0]] = \
                        other_spaces + "height = " + '-' + height + 'm'
                    # change instrument according to the met tower variable name
                    instrument_row = temp_attr_df[temp_attr_df['Text'].apply(lambda x:
                                                                             x.strip().startswith("instrument"))]
                    instrument = value['Instrument']
                    temp_attr_df.iloc[temp_attr_df.index == instrument_row.index[0]] = \
                        other_spaces + "instrument = " + instrument
                    # write the modified sections
                    variables_lines_out.extend(temp_attr_df['Text'].tolist())
                    variables_lines_out.extend(temp_xl_df['Text'].tolist())
                else:
                    log.warning("Variable %s not found in met_data sheet. Skipping variable", key)

        # return the variables mapping and output list
        return variables_lines_out, variable_ameriflux_mapping

    @staticmethod
    def format_ameriflux_var(df, var_start_end, ameriflux_key, full_output_variables, met_data_variables,
                             mainstem_variables_mapping, spaces=SPACES):
        """
            Change variable units for Ameriflux only variables

            Args:
                df (obj): Pandas dataframe with all variable lines from L1_ameriflux_only.txt
                var_start_end (list): List of tuple, the starting and ending index for each ameriflux variable
                ameriflux_key (obj): Pandas dataframe of AmeriFlux-Mainstem varible name sheet
                full_output_variables (list): List of full_output variable names
                met_data_variables (list): List of met_data variable names
                mainstem_variables_mapping (dict) : Mapping of mainstem variables
                spaces (str): Spaces to be inserted before each section and line
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l1_ameriflux
                variables_mapping (dict) : Mapping of variables to ameriflux-friendly variable names in L1
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_out = []  # variable lines to be written
        ameriflux_variables_mapping = {}
        # iterate over the variables
        for start, end in var_start_end:
            var_flag = False  # flag to see if variable has been changed or not
            # get variable, xl and attr sections as separate dataframes
            var, xl_df, attr_df = L1Format.get_var_xl_attr_df(df, start, end)
            var_name = var['Text'].iloc[0].strip('[]')  # get variable name
            # check if variable is already written to L1
            if (var_name in ameriflux_variables_mapping.keys()) or (var_name in ameriflux_variables_mapping.values()) \
                    or (var_name in mainstem_variables_mapping.keys()) or \
                    (var_name in mainstem_variables_mapping.values()):
                log.warning("Variable " + var_name + " is already written to L1. Skipping this variable.")
                continue
            # set the spacing for variable name line
            var_name_index = var.index[0]  # get index of variable name
            var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_name + "]]"
            ameriflux_variables_mapping[var_name] = var_name

            # get met tower variable name
            xl_name_row = xl_df[xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
            xl_var_name = xl_name_row['Text'].iloc[0].split('=')[1].strip()
            # get the corrected met tower variable name
            met_tower_var_name = L1Format.get_corrected_met_tower_var_name(xl_var_name)
            # get which sheet
            sheet_row = xl_df[xl_df['Text'].apply(lambda x: x.strip().startswith("sheet"))]
            sheet_name = sheet_row['Text'].iloc[0].split('=')[1].strip()

            # check if variable present in specified sheet
            if sheet_name.lower().startswith("full"):
                found_full_output = L1Format.check_variable_exists(met_tower_var_name, full_output_variables)
                if not found_full_output:
                    log.warning("Variable %s not found in full_output sheet. Skipping variable", met_tower_var_name)
                    continue
            elif sheet_name.lower().startswith("met"):
                found_met_data = L1Format.check_variable_exists(met_tower_var_name, met_data_variables)
                if not found_met_data:
                    log.warning("Variable %s not found in met_data sheet. Skipping variable", met_tower_var_name)
                    continue
            # format text as per L1
            xl_name_row_index = xl_name_row.index[0]
            xl_df['Text'].iloc[xl_df.index == xl_name_row_index] = "name = " + met_tower_var_name
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

            # update the variable df
            var.update(xl_df)
            var.update(attr_df)

            units_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("units"))]

            if ameriflux_key['Input sheet variable name'].isin([met_tower_var_name]).any():
                var_flag = True
                # check if var name should be changed for Ameriflux
                var_ameriflux_name = ameriflux_key.loc[ameriflux_key['Input sheet variable name'] == met_tower_var_name,
                                                       'Ameriflux variable name'].iloc[0]
                # add to the mapping, both met tower and original pyfluxpro names
                ameriflux_variables_mapping[var_name] = var_ameriflux_name
                ameriflux_variables_mapping[met_tower_var_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"
                if units_row.shape[0] > 0:
                    # check if units need to be changed
                    var_units_index = units_row.index[0]
                    var_ameriflux_units = \
                        ameriflux_key.loc[ameriflux_key['Ameriflux variable name'] == var_ameriflux_name,
                                          'Units after formatting'].iloc[0]
                    if not pd.isnull(var_ameriflux_units):
                        # if unit needs to be changed, if its not NaN in the ameriflux-mainstem sheet
                        # replace units only if it is not empty
                        # NOTES 12
                        var['Text'].iloc[var.index == var_units_index] = other_spaces + \
                                                                         "units = " + var_ameriflux_units
            if var_flag:
                variables_out.extend(var['Text'].tolist())

        # end of for loop
        return variables_out, ameriflux_variables_mapping
