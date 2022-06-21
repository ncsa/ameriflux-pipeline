# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/
import datetime

import pandas as pd
import re
import validators
from validators import ValidationFailure
import ipaddress
import os.path
import utils.data_util as data_util


class DataValidation:
    '''
    Class to implement data validation
    '''

    @staticmethod
    def integer_validation(data):
        """
        Method to check if the input data is a valid positive unsigned integer.
        Returns True if valid integer, else returns False
        Args:
            data: Input data to check for integer datatype
        Returns:
            (bool): True if integer datatype
        """
        return data.isdigit()

    @staticmethod
    def float_validation(data):
        """
        Method to check if the input data is a valid floating point number.
        Returns True if valid float, else returns False
        Args:
            data: Input data to check for float datatype
        Returns:
            (bool): True if float, else False
        """
        try:
            float(data)
            return True
        except ValueError:
            print(data, "not valid. Floating point expected")
            return False

    @staticmethod
    def string_validation(data):
        """
        Method to check if the input data is a valid string
        Returns True if valid string, else returns False
        Args:
            data: Input data to check for string datatype
        Returns:
            (bool): True if float, else False
        """
        return isinstance(data, str)

    @staticmethod
    def equality_validation(data1, data2):
        """
        Method to check if both inputs are equal.
        This method checks equality of value as well as data type and can be used with common data types.
        Returns True if equal, else returns False
        Args:
            data1: Input data 1 to check for equality
            data2: Input data 2 to check for equality
        Returns:
            (bool): True if equal, else False
        """
        return data1 == data2

    @staticmethod
    def url_validation(data):
        """
        Method to check if data is a url
        Returns True if valid url, else returns False
        Args:
            data (string): Input data to check for valid url
        Returns:
            (bool): True if url, else False
        """
        is_url = validators.url(data)
        if isinstance(is_url, ValidationFailure):
            print(data, "not valid. URL expected")
            return False
        return True

    @staticmethod
    def domain_validation(data):
        """
        Method to check if data is a domain or hostname
        Returns True if valid, else returns False
        Args:
            data (string): Input data to check for valid domain
        Returns:
            (bool): True if valid, else False
        """
        is_domain = validators.domain(data)
        if isinstance(is_domain, ValidationFailure):
            print(data, "not valid. Domain input expected")
            return False
        return True

    @staticmethod
    def ip_validation(data):
        """
        Method to check if data is a valid ip address
        Returns True if valid, else returns False
        Args:
            data (string): Input data to check for valid ip
        Returns:
            (bool): True if valid, else False
        """
        try:
            is_ip = ipaddress.ip_address(data)
        except ValueError:
            print(data, "not valid. IP address expected")
            return False
        return True

    @staticmethod
    def path_validation(data, type):
        """
        Method to check if both the data path is same as type
        Returns True if same, else returns False
        Args:
            data (str): Input path to check if directory or file
            type (str): Directory or file type
        Returns:
            (bool): True if path is same as type, else False
        """
        if type == 'dir':
            return os.path.isdir(data)
        elif type == 'file':
            return os.path.isfile(data)

    @staticmethod
    def filetype_validation(data, ext):
        """
        Method to check if both the data path is same as type
        Returns True if same, else returns False
        Args:
            data (str): Input file path with file extension to check if extension matches
            ext (str): Expected file extension
        Returns:
            (bool): True if file extension is same as expected, else False
        """
        # separate filename and extension
        filename, extension = os.path.splitext(data)
        if extension.lower() == ext.lower():
            return True
        else:
            print(data, "not valid." + ext + "extension expected")
            return False

    @staticmethod
    def datetime_validation(data):
        """
        Method to check if the the string is in valid datetime format YYYY-mm-dd HH:MM
        Returns True if valid, else returns False
        Args:
            data (str): Input string to check for valid datetime format
        Returns:
            (bool): True if valid, else False
        """
        try:
            datetime.datetime.strptime(data, "%Y-%m-%d HH:MM")
        except ValueError:
            print(data, "not in valid format of YYYY-mm-dd HH:MM")
            return False

    @staticmethod
    def is_empty_dir(data):
        """
        Method to check if the directory contains files
        Returns True if empty, else returns False
        Args:
            data (str): Input path to check if directory is empty
        Returns:
            (bool): True if directory is empty, else False
        """
        if os.listdir(data):
            return False
        else:
            return True

    @staticmethod
    def is_valid_meta_data(df):
        """
        Method to check if the input dataframe containing meta data of met tower variables is in valid format.
        Checks for expected meta data like TIMESTAMP and RECORD columns, TS and RN units and Min/Avg.
        These are standard if using Campbell datalogger.
        Returns True if valid, else returns False
        Args:
            df (obj): Pandas dataframe object to check for valid format
        Returns:
            (bool): True if df is valid, else False
        """
        # check for TIMESTAMP and RECORD columns in the first row
        column_names = df.iloc[0].to_list()
        if 'TIMESTAMP' not in column_names:
            print("TIMESTAMP not in met data.")
            return False
        unit_names = df.iloc[1].to_list()
        if 'TS' not in unit_names:
            print("TIMESTAMP expected unit TS not found in data")
            return False
        min_avg = df.iloc[2].to_list()
        if not ('Min' in min_avg or 'Avg' in min_avg):
            print("'Min' or 'Avg' keywords expected in third row of met data")
            return False
        # all validations done
        return True

    @staticmethod
    def is_valid_soils_key(df):
        """
        Method to check if the input soils key dataframe contains data as expected
        Checks for site name col, Datalogger/ met tower column, EddyPro and PyFluxPro columns
        Returns True if valid, else returns False
        Args:
            df (obj): Pandas dataframe object to check for valid soils key format
        Returns:
            (bool): True if df is valid, else False
        """
        site_name_col = df.filter(regex='Site name|site name|Site Name|Site|site').columns.to_list()
        if not site_name_col:
            print("Site name not in Soils key")
            return False
        # check if required columns are present
        req_cols = ['Datalogger/met water variable name', 'Datalogger/met temperature variable name',
                    'EddyPro temperature variable name', 'EddyPro water variable name',
                    'PyFluxPro water variable name', 'PyFluxPro temperature variable name']
        if set(req_cols) <= set(df.columns):
            # required columns is a subset of all column list
            return True
        else:
            print("Check for required columns in soils key: ", end='')
            print("Datalogger/met water variable name, Datalogger/met temperature variable name, "
                  "EddyPro temperature variable name, EddyPro water variable name, "
                  "PyFluxPro water variable name, PyFluxPro temperature variable name")
            return False

    @staticmethod
    def is_valid_full_output(df):
        """
        Method to check if the eddypro full output dataframe contains data as expected
        Checks for date, time, sonic_temperature and air_pressure columns
        Returns True if valid, else returns False
        Args:
            df (obj): Pandas dataframe object to check for valid eddypro full output sheet
        Returns:
            (bool): True if df is valid, else False
        """
        date_col = df.filter(regex="date|Date").columns.to_list()
        time_col = df.filter(regex="time|Time").columns.to_list()
        if not date_col:
            print("Date column not present in EddyPro full output sheet")
            return False
        if not time_col:
            print("Time column not present in EddyPro full output sheet")
            return False
        sonic_temperature_col = df.filter(regex="sonic_temperature").columns.to_list()
        if not sonic_temperature_col:
            print("Sonic temperature column not present in EddyPro full output sheet")
            return False
        air_pressure_col = df.filter(regex="air_pressure").columns.to_list()
        if not air_pressure_col:
            print("Air pressure column not present in EddyPro full output sheet")
            return False
        # all validations done
        return True

    @staticmethod
    def is_valid_ameriflux_mainstem_key(df):
        """
        Method to check if the Ameriflux-Mainstem key for PyFluxPro L1 formatting is as expected.
        Checks for columns : 'Original variable name', 'Ameriflux variable name', 'Units after formatting'
        Returns True if valid, else returns False
        Args:
            df (obj): Pandas dataframe object to check for valid erroring varaibles input sheet
        Returns:
            (bool): True if df is valid, else False
        """
        # check if required columns are present
        req_cols = ['Original variable name', 'Ameriflux variable name', 'Units after formatting']
        if set(req_cols) <= set(df.columns):
            # required columns is a subset of all column list
            return True
        else:
            print("Check for required columns in Amerilfux-Mainstem-Key: ", end='')
            print("Original variable name, Ameriflux variable name, Units after formatting")
            return False

    @staticmethod
    def is_valid_erroring_variables_key(df):
        """
        Method to check if the erroring variables key for PyFluxPro L1 formatting is as expected.
        Checks for Ameriflux label and PyFluxPro label columns
        Returns True if valid, else returns False
        Args:
            df (obj): Pandas dataframe object to check for valid erroring varaibles input sheet
        Returns:
            (bool): True if df is valid, else False
        """
        df.columns = df.columns.str.strip().str.lower()  # strip column names of extra spaces and convert to lowercase
        ameriflux_col = df.filter(regex="ameriflux").columns.to_list()
        pyfluxpro_col = df.filter(regex="pyfluxpro").columns.to_list()
        if not ameriflux_col:
            print("Ameriflux label column not present in L1 Erroring variables sheet")
            return False
        if not pyfluxpro_col:
            print("Pyfluxpro label column not present in L1 Erroring variables sheet")
            return False
        # all validations done
        return True



class L1Validation:
    '''
    Class to implement validation for L1 files
    '''

    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L1
    LEVEL_LINE = "level = L1"  # set the level

    # define patterns to match
    # variable names have alphanumeric characters and underscores with two square brackets
    VAR_PATTERN = '^\\[\\[[a-zA-Z0-9_]+\\]\\]$'
    XL_PATTERN = '^\\[\\[\\[xl\\]\\]\\]$'  # to match [[xl]] line
    ATTR_PATTERN = '^\\[\\[\\[Attr\\]\\]\\]$|^\\[\\[\\[attr\\]\\]\\]$'  # to match [[Attr]] or [[attr]] line
    UNITS_PATTERN = 'units'
    LONG_NAME_PATTERN = 'long_name'
    NAME_PATTERN = 'name'
    SHEET_PATTERN = 'sheet'

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
        if not L1Validation.check_level_line(line0):
            print("Incorrect format in Level section")
            return False
        # check Files section
        files_line_index = lines.index('[Files]\n')
        # check Global section
        global_line_index = lines.index('[Global]\n')
        # check Variables section
        variables_line_index = lines.index('[Variables]\n')
        if files_line_index and global_line_index:
            if L1Validation.check_files_line(lines[files_line_index + 1:global_line_index]):
                if L1Validation.check_global_line(lines[global_line_index + 1:variables_line_index]):
                    if L1Validation.check_variables_line(lines[variables_line_index + 1:]):
                        return True
                    else:
                        print("Incorrect format in L1 Variables section")
                        return False
                else:
                    print("Incorrect format in L1 Global section")
                    return False
            else:
                print("Incorrect format in L1 Files section")
                return False
        else:
            print("Undefined L1 Files and Global section")
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
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4:
                    # number of spaces is not as expected
                    return False
            if (line.strip().startswith('out_filename')):
                out_filename_flag = True  # found out_filename line
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4:
                    # number of spaces is not as expected
                    return False
            if file_path_flag and out_filename_flag:
                # test is completed, break out of for loop
                break
        if file_path_flag and out_filename_flag:
            return True
        else:
            return False

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
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4:
                    return False
            if acknowledgement_flag:
                # test is complete, break out of for loop
                break
        if acknowledgement_flag:
            return True
        else:
            return False

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
        var_count = 0  # counter for variables (var_pattern)
        for line in lines:
            if re.match(var_pattern, line.strip()):
                var_count += 1
                var_flag = True
                if L1Validation.check_space(line.rstrip()) != 4:
                    return False
            if re.match(xl_pattern, line.strip()):
                xl_flag = True
                if L1Validation.check_space(line.rstrip()) != 4 * 2:
                    return False
            if re.match(attr_pattern, line.strip()):
                attr_flag = True
                if L1Validation.check_space(line.rstrip()) != 4 * 2:
                    return False
            if (line.strip().startswith(units_pattern)):
                units_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(long_name_pattern)):
                long_name_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(name_pattern)):
                name_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if (line.strip().startswith(sheet_pattern)):
                sheet_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            # test if all flag values are true
            flags = [var_flag, xl_flag, attr_flag, units_flag, long_name_flag, name_flag, sheet_flag]
            if all(flags) and var_count == 1:
                # all flag values are true, then break out of for loop
                return True
            elif var_count > 1:
                print("Check first variable in Variables section")
                return False
        # end of for loop, format is as expected
        flags = [var_flag, xl_flag, attr_flag, units_flag, long_name_flag, name_flag, sheet_flag]
        if all(flags):
            # all flag values are true, then break out of for loop
            return True
        else:
            return False


class L2Validation:
    '''
    Class to implement validation for L2 files
    '''
    # define global variables
    SPACES = "    "  # set 4 spaces as default for a section in L2
    LEVEL_LINE = "level = L2"  # set the level
    VAR_PATTERN = '^\\[\\[[a-zA-Z0-9_]+\\]\\]$'  # variable name pattern
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'
    DEPENDENCYCHECK_PATTERN = '^ {8}\\[\\[\\[DependencyCheck\\]\\]\\]\n$'
    EXCLUDEDATES_PATTERN = '^ {8}\\[\\[\\[ExcludeDates\\]\\]\\]\n$'
    RANGECHECK_PATTERN = '^ {8}\\[\\[\\[RangeCheck\\]\\]\\]\n$'
    SOURCE_PATTERN = 'source'  # to match the source in DependencyCheck
    LOWER_PATTERN = 'lower'  # to match the lower in RangeCheck
    UPPER_PATTERN = 'upper'  # to match the lower in RangeCheck

    @staticmethod
    def check_l2_format(lines):
        """
            Check if the formatting for L1 is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        # check Level section
        line0 = lines[0].rstrip('\n')
        if not L2Validation.check_level_line(line0):
            print("Incorrect format in Level section")
            return False
        # check Variables section
        variables_line_index = lines.index('[Variables]\n')
        plots_line_index = lines.index('[Plots]\n')
        if variables_line_index and plots_line_index:
            if L2Validation.check_variables_line(lines[variables_line_index + 1:plots_line_index]):
                if L2Validation.check_plot_lines(lines[plots_line_index + 1:]):
                    return True
                else:
                    print("Incorrect format in L2 Plots section")
            else:
                print("Incorrect format in L2 Variables section")
                return False
        else:
            print("Undefined L2 Variables and Plots sections")
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
            if line_split[0].startswith('level') and line_split[1].strip() == 'L2':
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
    def check_variables_line(lines, var_pattern=VAR_PATTERN, dependencycheck_pattern=DEPENDENCYCHECK_PATTERN,
                             excludedates_pattern=EXCLUDEDATES_PATTERN, rangecheck_pattern=RANGECHECK_PATTERN,
                             source_pattern=SOURCE_PATTERN, lower_pattern=LOWER_PATTERN, upper_pattern=UPPER_PATTERN):
        """
            Check if the formatting for L2 Variables section is as expected
            Args:
                lines (list): List of strings. Lines in L1.txt
                var_pattern (str): Regex pattern to find the starting line for [Variables] section
                dependencycheck_pattern (str): Regex pattern to find the [[[DependencyCheck]]] section
                excludedates_pattern (str): Regex pattern to find the [[[ExcludeDates]]] section in Variables section
                rangecheck_pattern (str): Regex pattern to find the [[[RangeCheck]]] section in Variables
                source_pattern (str): Regex pattern to find the source line within DependencyCheck
                lower_pattern (str): Regex pattern to find the lower line within RangeCheck
                upper_pattern (str): Regex pattern to find the upper line within RangeCheck
            Returns:
                (bool) : Returns True if the format is as expected, else return False
        """
        # write the variables section to dataframe. this is used to get the indexes easily
        var_df = pd.DataFrame(lines, columns=['Text'])
        # remove newline and extra spaces from each line
        var_df['Text'] = var_df['Text'].apply(lambda x: x.strip())
        # get df with only variables and a list of variable start and end indexes
        variables, var_start_end = data_util.get_variables_index(var_df['Text'], var_pattern)
        # check if excludedates, rangecheck and dependencycheck follow the expected format
        # check if rangecheck has lower and upper. check if the number of comma seperated items are same for both
        # check if source line exists for DependencyCheck
        # check if excludedates has from and to dates that are comma separated and if the dates are valid
        for start, end in var_start_end:
            is_success = L2Validation.check_var_sections(lines[start:end], dependencycheck_pattern, rangecheck_pattern,
                                                         excludedates_pattern)
            if not is_success:
                print("Formatting issues in L2.txt between lines {} and {}".format(start, end))
                return False
        # all validations done
        return True

    @staticmethod
    def check_var_sections(lines, dependencycheck_pattern, rangecheck_pattern, excludedates_pattern):
        try:
            depcheck_line_index = lines.index(dependencycheck_pattern)
        except ValueError:
            depcheck_line_index = None
        try:
            rangecheck_line_index = lines.index(rangecheck_pattern)
        except ValueError:
            rangecheck_line_index = None
        try:
            excludedates_line_index = lines.index(excludedates_pattern)
        except ValueError:
            excludedates_line_index = None
        section_index = {'excludedates': excludedates_line_index, 'rangecheck': rangecheck_line_index,
                         'depcheck': depcheck_line_index}
        section_index = dict(sorted(section_index.items(), key=lambda item: (item[1] is None, item[1])))
        excludedates_section_index = list(section_index.keys()).index('excludedates')
        if excludedates_section_index == 2:
            excludedates_end_index = len(lines) - 1
        else:
            excludedates_end_index = list(section_index.values())[excludedates_section_index + 1]

        depcheck_flag, rangecheck_flag, excludedates_flag = False, False, False
        if depcheck_line_index and lines[depcheck_line_index+1].startswith('source'):
            depcheck_flag = True
        if rangecheck_line_index and lines[rangecheck_line_index+1].startswith('lower') and lines[rangecheck_line_index+2].startswith('upper'):
            lower_line = lines[rangecheck_line_index+1]
            upper_line = lines[rangecheck_line_index+2]
            lower_items = lower_line.split(',')
            upper_items = upper_line.split(',')
            rangecheck_flag = len(lower_items) == len(upper_items)
        if excludedates_line_index:
            for line in lines[excludedates_line_index:excludedates_end_index]:
                date_line = line.split('=')[1]
                dates = date_line.strip().split(',')
                start_date, end_date = dates[0], dates[1]
                print("Start end date", start_date, end_date)
                if DataValidation.datetime_validation(start_date) and DataValidation.datetime_validation(end_date):
                    excludedates_flag = True
                else:
                    excludedates_flag = False
                    print("Check dateformat in line", line)
                    break
        if depcheck_line_index and (not depcheck_flag):
            print("Check DependencyCheck section for variable".format(lines[0].strip()))
            return False
        elif rangecheck_line_index and (not rangecheck_flag):
            print("Check RangeCheck section for variable".format(lines[0].strip()))
            return False
        elif excludedates_line_index and (not excludedates_flag):
            print("Check ExcludeDates section for variable".format(lines[0].strip()))
            return False
        else:
            # all validations done
            return True

    @staticmethod
    def check_plot_lines(lines):
        return True


