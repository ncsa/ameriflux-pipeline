import pandas as pd
import os
import re

import utils.data_util as data_util


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
                        ameriflux_variable_user_confirmation, erroring_variable_key,
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
            ameriflux_variable_user_confirmation (str): User decision on whether to replace,
                                        ignore or ask during runtime in case of erroring variable names in PyFluxPro L1
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
        if not L1Format.check_l1_format(l1_mainstem_lines) or not L1Format.check_l1_format(l1_ameriflux_lines):
            print("Check L1.txt format")
            l1_mainstem_lines.close()
            l1_ameriflux_lines.close()
            return

        # read file_meta
        file_meta = pd.read_csv(file_meta_data_file)
        # get the site name
        file_site_name = file_meta.iloc[0][5]
        site_name = L1Format.get_site_name(file_site_name)
        df_soil_key = data_util.read_excel(soil_key)
        soil_moisture_labels, soil_temp_labels = L1Format.get_moisture_labels(site_name, df_soil_key)

        ameriflux_key = pd.read_excel(ameriflux_mainstem_key)  # read AmeriFlux-Mainstem variable name matching file

        # check if L1 erroring variable names need to be replaced or not
        ameriflux_variable_user_confirmation = ameriflux_variable_user_confirmation.lower()
        # by default we do not replace the erroring variables to ameriflux naming standards
        erroring_variable_flag = 'N'
        if ameriflux_variable_user_confirmation in ['a', 'ask']:
            print("Enter Y to replace L1 Erroring variable names to Ameriflux standards. Else enter N")
            erroring_variable_flag = input("Enter Y/N : ")
        elif ameriflux_variable_user_confirmation in ['n', 'no']:
            erroring_variable_flag = 'N'
        elif ameriflux_variable_user_confirmation in ['y', 'yes']:
            erroring_variable_flag = 'Y'

        if erroring_variable_flag.lower() in ['n', 'no']:
            # if user chose not to replace the variable name, read the name mapping
            # if this file is read, the instance becomes a dataframe, if not the variable type is a string
            erroring_variable_key = pd.read_excel(erroring_variable_key)  # read L1 erroring variable name matching file

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

        # get the variable lines to be written and variable name mapping
        variable_lines_out, ameriflux_variables = L1Format.format_variables(mainstem_var_df, mainstem_var_start_end,
                                                                            soil_moisture_labels, soil_temp_labels,
                                                                            ameriflux_key, erroring_variable_key)
        # write variables section lines to l1 output
        l1_output_lines.extend(variable_lines_out)

        # read from Ameriflux only L1 file
        ameriflux_variable_ind = L1Format.get_variable_line_index(l1_ameriflux_lines)
        ameriflux_var_lines = l1_ameriflux_lines[ameriflux_variable_ind + 1:]
        # get the list of ameriflux-friendly variables
        ameriflux_var_list = L1Format.get_ameriflux_variables(ameriflux_var_lines)
        # add to ameriflux_variables mapping
        for var in ameriflux_var_list:
            ameriflux_variables[var] = var

        # write output lines to file
        L1Format.write_list_to_file(l1_output_lines, l1_ameriflux_output)

        # close files
        l1_mainstem.close()
        l1_ameriflux.close()

        return ameriflux_variables

    @staticmethod
    def check_l1_format(lines):
        """
            Check if the formatting for L1 is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        # check Level section
        line0 = lines[0].rstrip('\n')
        if not L1Format.check_level_line(line0):
            print("Incorrect format in Level section")
            return False
        # check Files section
        files_line_index = lines.index('[Files]\n')
        # check Global section
        global_line_index = lines.index('[Global]\n')
        # check Variables section
        variables_line_index = lines.index('[Variables]\n')
        if files_line_index and global_line_index:
            if L1Format.check_files_line(lines[files_line_index + 1:global_line_index]):
                if L1Format.check_global_line(lines[global_line_index + 1:variables_line_index]):
                    if L1Format.check_variables_line(lines[variables_line_index + 1:]):
                        return True
                    else:
                        print("Incorrect format in Variables section")
                        return False
                else:
                    print("Incorrect format in Global section")
                    return False
            else:
                print("Incorrect format in Files section")
                return False
        else:
            print("Undefined Files and Global section")
            return False

    @staticmethod
    def check_level_line(line):
        """
            Check if the formatting for L1 Level section is as expected
            Args:
                line (str): Level line from input L1.txt
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        if line:
            line_split = line.split('=')
            if line_split[0].startswith('level') and line_split[1].strip() == 'L1':
                return True
        return False

    @staticmethod
    def check_space(test_string):
        """
            Count number of spaces in the string
            Args:
                test_string (str): Input string
            Returns:
                (int) : Returns the count of empty spaces in the string
        """
        return test_string.count(" ")

    @staticmethod
    def check_files_line(lines):
        """
            Check if the formatting for L1 Files section is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        file_path_flag = False  # flag for file_path line
        out_filename_flag = False  # flag for out_filename line
        for line in lines:
            if (line.strip().startswith('file_path')):
                file_path_flag = True  # found file_path line
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4:
                    # number of spaces is not as expected
                    return False
            if (line.strip().startswith('out_filename')):
                out_filename_flag = True  # found out_filename line
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4:
                    # number of spaces is not as expected
                    return False
            if file_path_flag and out_filename_flag:
                # test is completed, break out of for loop
                break
        return True

    @staticmethod
    def check_global_line(lines):
        """
            Check if the formatting for L1 Global section is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        acknowledgement_flag = False  # flag for acknowledgement line
        for line in lines:
            if (line.strip().startswith('acknowledgement')):
                acknowledgement_flag = True  # found acknowledgment line
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4:
                    return False
            if acknowledgement_flag:
                # test is complete, break out of for loop
                break
        return True

    @staticmethod
    def check_variables_line(lines, var_pattern=VAR_PATTERN, xl_pattern=XL_PATTERN, attr_pattern=ATTR_PATTERN,
                             units_pattern=UNITS_PATTERN, long_name_pattern=LONG_NAME_PATTERN,
                             name_pattern=NAME_PATTERN, sheet_pattern=SHEET_PATTERN):
        """
            Check if the formatting for L1 Variables section is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
                var_pattern (str): Regex pattern to find the starting line for [Variables] section
                xl_pattern (str): Regex pattern to find the [[[xl]]] section within Variables section
                attr_pattern (str): Regex pattern to find the [[[Attr]]] section within Variables section
                units_pattern (str): Regex pattern to find the units line within Attr section
                long_name_pattern (str): Regex pattern to find the long_name line within Attr section
                name_pattern (str): Regex pattern to find the name line within Attr section
                sheet_pattern (str): Regex pattern to find the sheet line within xl section
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        # define flags for pattern matching line
        var_flag = False
        xl_flag = False
        attr_flag = False
        units_flag = False
        long_name_flag = False
        name_flag = False
        sheet_flag = False
        for line in lines:
            if re.match(var_pattern, line.strip()):
                var_flag = True
                if L1Format.check_space(line.rstrip()) != 4:
                    return False
            if re.match(xl_pattern, line.strip()):
                xl_flag = True
                if L1Format.check_space(line.rstrip()) != 4 * 2:
                    return False
            if re.match(attr_pattern, line.strip()):
                attr_flag = True
                if L1Format.check_space(line.rstrip()) != 4 * 2:
                    return False
            if (line.strip().startswith(units_pattern)):
                units_flag = True
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(long_name_pattern)):
                long_name_flag = True
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(name_pattern)):
                name_flag = True
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(sheet_pattern)):
                sheet_flag = True
                if L1Format.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            # test if all flag values are true
            flags = [var_flag, xl_flag, attr_flag, units_flag, long_name_flag, name_flag, sheet_flag]
            if all(flags):
                # all flag values are true, then break out of for loop
                break
        # end of for loop, format is as expected
        return True

    @staticmethod
    def get_site_name(file_site_name):
        """
        Match the file site name to site names in soil key data.
        From the input file site name, return the matching site name
        Site name is used as lookup in soil key table

        Args:
            file_site_name (str): file site name from file meta data, first row of input met file
        Returns:
            (str): matching site name
        """
        if re.match('^CPU:Maize_Control_*', file_site_name):
            return 'Maize-Control'
        elif re.match('^CPU:Maize_*', file_site_name):
            return 'Maize-Basalt'
        elif re.match('^CPU:Miscanthus_Control_*', file_site_name):
            return 'Miscanthus-Control'
        elif re.match('^CPU:Miscanthus_*', file_site_name):
            return 'Miscanthus-Basalt'
        elif re.match('^CPU:Sorghum_*', file_site_name):
            return 'Sorghum'

    @staticmethod
    def get_moisture_labels(site_name, df_soil_key):
        """
        Method to get a mapping from PyFluxPro labels to Ameriflux labels
        Args :
            site_name (str): Name of site used to filter the soil variables
            df_soil_key (obj): soil key dataframe containing the mapping between variable labels
        Returns :
            soil_moisture_labels (dict): Soil moisture variable mapping from pyfluxpro to ameriflux labels
            soil_temp_labels (dict): Soil temperature variable mapping from pyfluxpro to ameriflux labels
        """
        site_soil_key = df_soil_key[df_soil_key['Site name'] == site_name]  # get all variables for the site
        # get soil temp and moisture variables
        site_soil_moisture = site_soil_key[['PyFluxPro water variable name', 'EddyPro water variable name']]
        site_soil_temp = site_soil_key[['PyFluxPro temperature variable name', 'EddyPro temperature variable name']]

        col_rename = {'PyFluxPro water variable name': 'PyFluxPro label',
                      'PyFluxPro temperature variable name': 'PyFluxPro label',
                      'EddyPro water variable name': 'Ameriflux label',
                      'EddyPro temperature variable name': 'Ameriflux label'}
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
    def get_ameriflux_variables(lines, pattern = VAR_PATTERN_WITH_SPACE):
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
        for i in range(len(variables.index) - 1):
            start_ind = variables.index[i]
            end_ind = variables.index[i + 1]
            var_start_end.append((start_ind, end_ind))
        var_start_end.append((end_ind, text.last_valid_index()))  # append the start and end index of the last variable
        return variables, var_start_end

    @staticmethod
    def format_variables(df, var_start_end, moisture_labels, temp_labels, ameriflux_key, erroring_variable_key,
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
                ameriflux_variables (dict) : Mapping of pyfluxpro-friendly to ameriflux-friendly variable names in L1
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_lines_out = []  # variable lines to be written
        # mapping for variables to be written
        ameriflux_variables = {}  # dictionary of pyfluxpro-friendly names to ameriflux-friendly names

        # iterate over the variables
        for start, end in var_start_end:
            var_flag = False  # flag to see if variable has been changed or not
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

            # format text as per L1
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

            var.update(xl_df)
            var.update(attr_df)

            units_row = attr_df[attr_df['Text'].apply(lambda x: x.strip().startswith("units"))]

            # check if the variable is one of the erroring variables in L1 PyFluxPro
            # check if the erroring_variable_key is a dataframe.
            if isinstance(erroring_variable_key, pd.DataFrame) and \
                    erroring_variable_key['PyFluxPro label'].isin([var_name]).any():
                # the variable name is one of the erroring variables.
                # do not replace the variable name with ameriflux label
                var_flag = True
                var_name_index = var.index[0]
                ameriflux_variables[var_name] = var_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_name + "]]"

            # if the erroring variable is to be replaced, the Ameriflux friendly variable name is in ameriflux_key
            elif ameriflux_key['Original variable name'].isin([var_name]).any():
                var_flag = True
                # check if var name should be changed for Ameriflux
                var_name_index = var.index[0]
                var_ameriflux_name = ameriflux_key.loc[ameriflux_key['Original variable name'] == var_name,
                                                       'Ameriflux variable name'].iloc[0]
                ameriflux_variables[var_name] = var_ameriflux_name
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
                var_flag = True
                var_name_index = var.index[0]
                var_ameriflux_name = moisture_labels[var_name]
                ameriflux_variables[var_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"
                # change the unit to percentage
                if units_row.shape[0] > 0:
                    var_units_index = units_row.index[0]
                    var['Text'].iloc[var.index == var_units_index] = other_spaces + "units = " + '%'

            # check if variable is soil temp
            elif var_name.startswith("Ts_"):
                var_flag = True
                var_name_index = var.index[0]
                var_ameriflux_name = temp_labels[var_name]
                ameriflux_variables[var_name] = var_ameriflux_name
                var['Text'].iloc[var.index == var_name_index] = var_spaces + "[[" + var_ameriflux_name + "]]"

            if var_flag:
                variables_lines_out.extend(var['Text'].tolist())

        # end of for loop
        return variables_lines_out, ameriflux_variables

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
        """
        # define spaces for formatting in L1
        var_spaces = spaces
        attr_spaces = spaces + spaces
        xl_spaces = spaces + spaces
        other_spaces = spaces + spaces + spaces

        variables_out = []  # variable lines to be written
        # iterate over the variables
        for start, end in var_start_end:
            var_flag = False  # flag to see if variable has been changed or not
            # get each variable in a separate df
            var = df[start:end]
            var_name = var['Text'].iloc[0].strip('[]')
            # get the [[[xl]]] section
            xl = var[var['Text'].str.contains(xl_pattern)]
            xl_df = df[xl.index[0]:end]
            # format text as per L1
            xl_df['Text'].iloc[0] = xl_spaces + xl_df['Text'].iloc[0]
            xl_df['Text'].iloc[1:] = other_spaces + xl_df['Text'].iloc[1:]

            # get the [[[Attr]]] OR [[[attr]]] section
            attr = var[var['Text'].str.contains(attr_pattern)]
            attr_df = df[attr.index[0]:xl.index[0]]
            # format text as per L1
            attr_df['Text'].iloc[0] = attr_spaces + attr_df['Text'].iloc[0]
            attr_df['Text'].iloc[1:] = other_spaces + attr_df['Text'].iloc[1:]

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
        return variables_out

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
            print("AmeriFlux L1 saved in ", outfile)
        except Exception:
            raise Exception("Failed to create file ", outfile)

