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
    # variable name lines starts with 4 spaces and ends with new line
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'
    XL_PATTERN = '^\\[\\[\\[xl\\]\\]\\]$'  # to match [[xl]] line
    ATTR_PATTERN = '^\\[\\[\\[Attr\\]\\]\\]$|^\\[\\[\\[attr\\]\\]\\]$'  # to match [[Attr]] or [[attr]] line
    UNITS_PATTERN = 'units'
    LONG_NAME_PATTERN = 'long_name'
    NAME_PATTERN = 'name'
    SHEET_PATTERN = 'sheet'

    # main method which calls other functions
    @staticmethod
    def data_formatting(pyfluxpro_input, l1_mainstem, l1_ameriflux_only, ameriflux_mainstem_key, file_meta_data_file,
                        soil_key, outfile, l1_ameriflux_output,
                        erroring_variable_flag, erroring_variable_key,
                        met_eddypro_soil_temp_labels, met_eddypro_soil_moisture_labels,
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
            soil_key (str) : A file path for input soil key sheet
            outfile (str): A file path for the output of L1 run. This typically has .nc extension
            l1_ameriflux_output (str): A file path for the L1.txt that is formatted for Ameriflux standards
            erroring_variable_flag (str): A flag denoting whether some PyFluxPro variables (erroring variables) are
                                        renamed to Ameriflux labels in L1. Y is renamed, N if not. By default it is N.
            erroring_variable_key (str): Variable name key used to match the original variable names to Ameriflux names
                                        for variables throwing an error in PyFluxPro L1.
                                        This is an excel file named L1_erroring_variables.xlsx
            spaces (str): Spaces to be inserted before each section and line
            level_line (str): Line specifying the level. L1 for this section.
        Returns:
            dict: Mapping of pyfluxpro-friendly label to Ameriflux-friendly labels for variables in L1_Ameriflux.txt
        """
        # open input file in read mode
        l1_mainstem = open(l1_mainstem, 'r')
        l1_ameriflux = open(l1_ameriflux_only, 'r')
        l1_output_lines = []  # comma separated list of lines to be written
        # read lines from l1 inputs
        l1_mainstem_lines = l1_mainstem.readlines()
        l1_ameriflux_lines = l1_ameriflux.readlines()

        # check if input L1 have the same format as expected
        if not L1Validation.check_l1_format(l1_mainstem_lines) or not L1Validation.check_l1_format(l1_ameriflux_lines):
            log.error("Check L1.txt format")
            l1_mainstem.close()
            l1_ameriflux.close()
            return None

        # read file_meta
        file_meta = pd.read_csv(file_meta_data_file)
        # get the site name
        file_site_name = file_meta.iloc[0][5]
        site_name = data_util.get_site_name(file_site_name)
        df_soil_key = data_util.read_excel(soil_key)
        if not DataValidation.is_valid_soils_key(df_soil_key):
            log.error("Soils_key.xlsx file invalid format.")
            return None
        soil_moisture_labels, soil_temp_labels = L1Format.get_soil_labels(site_name, df_soil_key)

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
        mainstem_global_lines, mainstem_variable_ind = L1Format.get_global_lines(l1_mainstem_lines)
        ameriflux_global_lines, ameriflux_variable_ind = L1Format.get_global_lines(l1_ameriflux_lines)
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
        variable_lines_out, mainstem_variables_mapping = L1Format.format_variables(mainstem_var_df,
                                                                                   mainstem_var_start_end,
                                                                                   soil_moisture_labels,
                                                                                   soil_temp_labels,
                                                                                   ameriflux_key, erroring_variable_key,
                                                                                   met_eddypro_soil_temp_labels,
                                                                                   met_eddypro_soil_moisture_labels)
        # write variables section lines to l1 output
        l1_output_lines.extend(variable_lines_out)

        # read from Ameriflux only L1 file
        ameriflux_var_df = pd.DataFrame(l1_ameriflux_lines[ameriflux_variable_ind + 1:], columns=['Text'])
        # remove newline and extra spaces from each line
        ameriflux_var_df['Text'] = ameriflux_var_df['Text'].apply(lambda x: x.strip())
        # get df with only variables and a list of variable start and end indexes
        ameriflux_variables, ameriflux_var_start_end = L1Format.get_variables_index(ameriflux_var_df['Text'])
        # get the variable lines to be written
        variable_lines_out, ameriflux_variables_mapping = L1Format.format_ameriflux_var_units(ameriflux_var_df,
                                                                                              ameriflux_var_start_end,
                                                                                              ameriflux_key)

        # create dictionary mapping of variables . pyfluxpro labels : ameriflux labels
        variable_mapping = mainstem_variables_mapping.copy()
        variable_mapping.update(ameriflux_variables_mapping)

        # write variables section lines to l1 output
        l1_output_lines.extend(variable_lines_out)

        # write output lines to file
        log.info("Writting Ameriflux L1 control file to " + l1_ameriflux_output)
        data_util.write_list_to_file(l1_output_lines, l1_ameriflux_output)

        # close files
        l1_mainstem.close()
        l1_ameriflux.close()

        # return pyfluxpro to ameriflux label mapping
        return variable_mapping

    @staticmethod
    def get_soil_labels(site_name, df_soil_key):
        """
        Method to get a mapping from PyFluxPro labels to Ameriflux labels
        Args :
            site_name (str): Name of site used to filter the soil variables
            df_soil_key (obj): soil key dataframe containing the mapping between variable labels
        Returns :
            soil_moisture_labels (dict): Soil moisture variable mapping from pyfluxpro to ameriflux labels
            soil_temp_labels (dict): Soil temperature variable mapping from pyfluxpro to ameriflux labels
        """
        site_name_col = df_soil_key.filter(regex=re.compile("^name|^site", re.IGNORECASE)).columns.to_list()[0]
        site_soil_key = df_soil_key[df_soil_key[site_name_col] == site_name]  # get all variables for the site

        # get column names matching pyfluxpro
        pyfluxpro_cols = site_soil_key.filter(regex=re.compile("^pyfluxpro", re.IGNORECASE)).columns.to_list()
        # get column names matching eddypro
        eddypro_cols = site_soil_key.filter(regex=re.compile("^eddypro", re.IGNORECASE)).columns.to_list()
        # remove variable columns that have 'old' in the name
        old_pattern = re.compile(r'old', re.IGNORECASE)
        pyfluxpro_cols = list(filter(lambda x: not old_pattern.search(x), pyfluxpro_cols))
        eddypro_cols = list(filter(lambda x: not old_pattern.search(x), eddypro_cols))
        # get temp and water variable columns from the above column list
        temp_pattern = re.compile(r'temperature|temp', re.IGNORECASE)
        water_pattern = re.compile(r"water|moisture", re.IGNORECASE)
        pyfluxpro_temp_col = list(filter(temp_pattern.search, pyfluxpro_cols))
        pyfluxpro_water_col = list(filter(water_pattern.search, pyfluxpro_cols))
        eddypro_temp_col = list(filter(temp_pattern.search, eddypro_cols))
        eddypro_water_col = list(filter(water_pattern.search, eddypro_cols))
        # get soil temp and moisture variables
        site_soil_moisture = site_soil_key[[pyfluxpro_water_col[0], eddypro_water_col[0]]]
        site_soil_temp = site_soil_key[[pyfluxpro_temp_col[0], eddypro_temp_col[0]]]
        col_rename = {pyfluxpro_water_col[0]: 'PyFluxPro label', pyfluxpro_temp_col[0]: 'PyFluxPro label',
                      eddypro_water_col[0]: 'Ameriflux label', eddypro_temp_col[0]: 'Ameriflux label'}
        site_soil_moisture.rename(columns=col_rename, inplace=True)
        site_soil_temp.rename(columns=col_rename, inplace=True)

        # make these variable labels as dictionary
        soil_moisture_labels = site_soil_moisture.set_index('PyFluxPro label').T.to_dict('list')
        soil_temp_labels = site_soil_temp.set_index('PyFluxPro label').T.to_dict('list')

        # remove list from values
        for key, value in soil_moisture_labels.items():
            soil_moisture_labels[key] = ''.join(value)
        for key, value in soil_temp_labels.items():
            soil_temp_labels[key] = ''.join(value)

        return soil_moisture_labels, soil_temp_labels

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
        # get units column
        units_col = df_ameriflux_key.filter(regex=re.compile("^units", re.IGNORECASE)).columns.to_list()
        # rename columns
        df_ameriflux_key.rename(columns={ameriflux_cols[0]: 'Ameriflux variable name',
                                         original_cols[0]: 'Original variable name',
                                         units_col[0]: 'Units after formatting'}, inplace=True)

        return df_ameriflux_key

    @staticmethod
    def get_global_lines(lines, spaces=SPACES):
        """
            Get Global section from L1.txt

            Args:
                lines (list): List of the strings that are read fom L1.txt
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
                if line.strip() == "[Variables]":
                    global_start_writing = False
                    return global_lines, ind
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
    def format_variables(df, var_start_end, moisture_labels, temp_labels, ameriflux_key, erroring_variable_key,
                         met_eddypro_soil_temp_labels, met_eddypro_soil_moisture_labels,
                         spaces=SPACES, xl_pattern=XL_PATTERN, attr_pattern=ATTR_PATTERN):
        """
            Change variable names and units to AmeriFlux standard

            Args:
                df (obj): Pandas dataframe with all variable lines from L1_mainstem.txt
                var_start_end (list): List of tuple, the starting and ending index for each variable
                moisture_labels (dict) : Mapping from pyfluxpro to ameriflux labels for soil moisture
                temp_labels (dict): Mapping from pyfluxpro to ameriflux labels for soil temperature
                ameriflux_key (obj): Pandas dataframe of AmeriFlux-Mainstem varible name sheet
                erroring_variable_key (str/obj): Variable name key used to match the original variable names to
                                        Ameriflux names for variables throwing an error in PyFluxPro L1.
                spaces (str): Spaces to be inserted before each section and line
                xl_pattern (str): Regex pattern to find the [[[xl]]] section within Variables section
                attr_pattern (str): Regex pattern to find the [[[Attr]]] section within Variables section
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l1_ameriflux
                variables_mapping (dict) : Mapping of pyfluxpro-friendly to ameriflux-friendly variable names in L1
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_lines_out = []  # variable lines to be written
        # mapping for variables to be written
        variables_mapping = {}  # dictionary of pyfluxpro-friendly names to ameriflux-friendly names

        # iterate over the variables
        for start, end in var_start_end:
            # NOTES 13
            var_flag = False  # flag to see if variable is to be written or not
            # get each variable in a separate df
            var = df[start:end]
            var_name = var['Text'].iloc[0].strip('[]')

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

            units_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("unit"))]

            # check if the variable is one of the erroring variables in L1 PyFluxPro
            # check if the erroring_variable_key is a dataframe.
            if isinstance(erroring_variable_key, pd.DataFrame) and \
                    erroring_variable_key['PyFluxPro label'].isin([var_name]).any():
                # the variable name is one of the erroring variables.
                # do not replace the variable name with ameriflux label
                var_flag = True
                var_name_index = var.index[0]
                variables_mapping[var_name] = var_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_name + "]]"

            # if the erroring variable is to be replaced, the Ameriflux friendly variable name is in ameriflux_key
            elif ameriflux_key['Original variable name'].isin([var_name]).any():
                var_flag = True
                # check if var name should be changed for Ameriflux
                var_name_index = var.index[0]
                var_ameriflux_name = ameriflux_key.loc[ameriflux_key['Original variable name'] == var_name,
                                                       'Ameriflux variable name'].iloc[0]
                variables_mapping[var_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"

                if units_row.shape[0] > 0:
                    # check if units need to be changed
                    var_units_index = units_row.index[0]
                    var_ameriflux_units = \
                        ameriflux_key.loc[ameriflux_key['Original variable name'] == var_name,
                                          'Units after formatting'].iloc[0]
                    if not pd.isnull(var_ameriflux_units):
                        # if unit needs to be changed, if its not NaN in the ameriflux-mainstem sheet
                        # replace units only if it is not empty
                        var['Text'].iloc[var.index == var_units_index] = other_spaces + \
                                                                         "units = " + var_ameriflux_units
            # check if variable is soil moisture
            elif var_name.startswith("Sws_"):
                # get moisture variable lines
                moisture_xl_df = xl_df
                moisture_attr_df = attr_df
                # format moisture variable lines
                var_name_index = var.index[0]
                # get the met tower variable name from xl line and compare with met_eddypro_soil_moisture_labels
                met_tower_var_name = xl_df['Text'].iloc[1].split('=')[1].strip()
                # get ameriflux name. returns None if not found
                var_ameriflux_name = met_eddypro_soil_moisture_labels.get(met_tower_var_name)
                if var_ameriflux_name is not None:
                    # write only if ameriflux name is found
                    var_flag = True
                    # delete key from labels
                    del met_eddypro_soil_moisture_labels[met_tower_var_name]
                    variables_mapping[var_name] = var_ameriflux_name
                    var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"
                    # change the unit to percentage
                    if units_row.shape[0] > 0:
                        var_units_index = units_row.index[0]
                        attr_df['Text'].iloc[var_units_index] = other_spaces + "units = " + '%'
                    # correct the height row
                    height_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("height"))]
                    var_height_index = height_row.index[0]
                    # get number in ameriflux var name to get height
                    attr_height = [str(x) for x in var_ameriflux_name if x.isdigit()]
                    attr_height = ''.join(attr_height)
                    # round height to one decimal place and convert to string
                    moisture_height = str(round(int(attr_height)/100, 1))
                    attr_df['Text'].iloc[var_height_index] = other_spaces + "height = " + '-' + moisture_height + 'm'

            # check if variable is soil temp
            elif var_name.startswith("Ts_"):
                # get temp variable lines
                temp_xl_df = xl_df
                temp_attr_df = attr_df
                # format temp variable lines
                var_name_index = var.index[0]
                # get the met tower variable name from xl line and compare with met_eddypro_soil_temp_labels
                met_tower_var_name = xl_df['Text'].iloc[1].split('=')[1].strip()
                var_ameriflux_name = met_eddypro_soil_temp_labels.get(met_tower_var_name)
                if var_ameriflux_name is not None:
                    var_flag = True
                    # delete key from labels
                    del met_eddypro_soil_temp_labels[met_tower_var_name]
                    var_ameriflux_name = var_ameriflux_name.upper()
                    variables_mapping[var_name] = var_ameriflux_name
                    var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"

            # format text as per L1
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

            # update the variable df
            var.update(xl_df)
            var.update(attr_df)

            if var_flag:
                variables_lines_out.extend(var['Text'].tolist())

        # end of for loop
        # if there are variables left in the labels, write them to the variables sheet
        if len(met_eddypro_soil_moisture_labels) > 0:
            for key, value in met_eddypro_soil_moisture_labels.items():
                variables_lines_out.append(var_spaces + "[[" + value + "]]")
                name_row = moisture_xl_df[moisture_xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
                moisture_xl_df.iloc[name_row.index[0]]['Text'] = other_spaces + "name = " + key
                height_row = moisture_attr_df[moisture_attr_df['Text'].apply(lambda x: x.strip().startswith("height"))]
                attr_height = [str(x) for x in value if x.isdigit()]
                attr_height = ''.join(attr_height)
                # round height to one decimal place and convert to string
                moisture_height = str(round(int(attr_height) / 100, 1))
                moisture_attr_df.iloc[height_row.index[0]]['Text'] = \
                    other_spaces + "height = " + '-' + moisture_height + 'm'
                # change instrument according to the met tower variable name
                instrument_row = moisture_attr_df[moisture_attr_df['Text'].apply(lambda x:
                                                                                 x.strip().startswith("instrument"))]
                if key.startswith("Moisture"):
                    moisture_attr_df.iloc[instrument_row.index[0]]['Text'] = \
                        other_spaces + "instrument = " + 'Hydra probe'
                else:
                    moisture_attr_df.iloc[instrument_row.index[0]]['Text'] = \
                        other_spaces + "instrument = " + 'soilVUE'
                variables_lines_out.extend(moisture_attr_df['Text'].tolist())
                variables_lines_out.extend(moisture_xl_df['Text'].tolist())
        if len(met_eddypro_soil_temp_labels) > 0:
            for key, value in met_eddypro_soil_temp_labels.items():
                variables_lines_out.append(var_spaces + "[[" + value + "]]")
                name_row = temp_xl_df[temp_xl_df['Text'].apply(lambda x: x.strip().startswith("name"))]
                temp_xl_df.iloc[name_row.index[0]]['Text'] = other_spaces + "name = " + key
                height_row = moisture_attr_df[moisture_attr_df['Text'].apply(lambda x: x.strip().startswith("height"))]
                attr_height = [str(x) for x in value if x.isdigit()]
                attr_height = ''.join(attr_height)
                # round height to one decimal place and convert to string
                moisture_height = str(round(int(attr_height) / 100, 1))
                moisture_attr_df.iloc[height_row.index[0]]['Text'] = \
                    other_spaces + "height = " + '-' + moisture_height + 'm'
                # change instrument according to the met tower variable name
                instrument_row = moisture_attr_df[moisture_attr_df['Text'].apply(lambda x:
                                                                                 x.strip().startswith("instrument"))]
                if key.startswith("Moisture"):
                    moisture_attr_df.iloc[instrument_row.index[0]]['Text'] = \
                        other_spaces + "instrument = " + 'Hydra probe'
                else:
                    moisture_attr_df.iloc[instrument_row.index[0]]['Text'] = \
                        other_spaces + "instrument = " + 'soilVUE'
                variables_lines_out.extend(moisture_attr_df['Text'].tolist())
                variables_lines_out.extend(moisture_xl_df['Text'].tolist())


        return variables_lines_out, variables_mapping

    @staticmethod
    def format_ameriflux_var_units(df, var_start_end, ameriflux_key,
                                   spaces=SPACES, xl_pattern=XL_PATTERN, attr_pattern=ATTR_PATTERN):
        """
            Change variable units for Ameriflux only variables

            Args:
                df (obj): Pandas dataframe with all variable lines from L1_ameriflux_only.txt
                var_start_end (list): List of tuple, the starting and ending index for each ameriflux variable
                ameriflux_key (obj): Pandas dataframe of AmeriFlux-Mainstem varible name sheet
                spaces (str): Spaces to be inserted before each section and line
                xl_pattern (str): Regex pattern to find the [[[xl]]] section within Variables section
                attr_pattern (str): Regex pattern to find the [[[Attr]]] section within Variables section
            Returns:
                variable_lines_out (list) : List of variables lines to be written to l1_ameriflux
                variables_mapping (dict) : Mapping of pyfluxpro-friendly to ameriflux-friendly variable names in L1
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_out = []  # variable lines to be written
        variables_mapping = {}
        # iterate over the variables
        for start, end in var_start_end:
            var_flag = False  # flag to see if variable has been changed or not
            # get each variable in a separate df
            var = df[start:end]
            var_name = var['Text'].iloc[0].strip('[]')

            # set the spacing for variable name line
            var_name_index = var.index[0]
            var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_name + "]]"
            variables_mapping[var_name] = var_name

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

            # format text as per L1
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

            # update the variable df
            var.update(xl_df)
            var.update(attr_df)

            units_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("units"))]

            if ameriflux_key['Ameriflux variable name'].isin([var_name]).any():
                var_flag = True
                if units_row.shape[0] > 0:
                    # check if units need to be changed
                    var_units_index = units_row.index[0]
                    var_ameriflux_units = \
                        ameriflux_key.loc[ameriflux_key['Ameriflux variable name'] == var_name,
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
        return variables_out, variables_mapping
