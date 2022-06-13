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
from pandas.api.types import is_datetime64_any_dtype as is_datetime64
import ipaddress
import os.path


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
        site_name_col = df.filter(regex='Site name|site name|Site Name|Site|site').columns.to_list()[0]
        if not site_name_col:
            print("Site name not in Soils key")
            return False
        # check if required columns are present
        req_cols = ['Datalogger/met water variable name', 'Datalogger/met temperature variable name',
<<<<<<< HEAD:ameriflux_pipeline/utils/data_validation.py
                    'EddyPro temperature variable name', 'EddyPro water variable name',
                    'PyFluxPro water variable name', 'PyFluxPro temperature variable name']
=======
                    'EddyPro temperature variable name', 'EddyPro water variable name']
>>>>>>> b83454dc5ce92e1522b55b1d81b60473a36fa7d3:ameriflux_pipeline/utils/validation.py
        if set(req_cols) <= set(df.columns):
            # required columns is a subset of all column list
            return True
        else:
            print("Check for required columns in soils key: ", end='')
            print("Datalogger/met water variable name, Datalogger/met temperature variable name, "
                  "EddyPro temperature variable name, EddyPro water variable name")
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
<<<<<<< HEAD:ameriflux_pipeline/utils/data_validation.py

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
    # variable name lines starts with 4 spaces and ends with new line
    VAR_PATTERN_WITH_SPACE = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'
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
        flags = [var_flag, xl_flag, attr_flag, units_flag, long_name_flag, name_flag, sheet_flag]
        for line in lines:
            if re.match(var_pattern, line.strip()):
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
            if all(flags):
                # all flag values are true, then break out of for loop
                return True
        # end of for loop, format is as expected
        if all(flags):
            # all flag values are true, then break out of for loop
            return True
        else:
            return False
=======
>>>>>>> b83454dc5ce92e1522b55b1d81b60473a36fa7d3:ameriflux_pipeline/utils/validation.py
