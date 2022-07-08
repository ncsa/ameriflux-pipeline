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
import logging

# create log object with current module name
log = logging.getLogger(__name__)


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
            log.error("%s not valid. Floating point expected", data)
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
            log.error("%s not valid. URL expected", data)
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
            log.error("%s not valid. Domain input expected", data)
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
            log.error("%s not valid. IP address expected", data)
            return False
        return True

    @staticmethod
    def path_validation(data, data_type):
        """
        Method to check if both the data path is same as type
        Returns True if same, else returns False
        Args:
            data (str): Input path to check if directory or file
            data_type (str): Directory or file type
        Returns:
            (bool): True if path is same as type, else False
        """
        if data_type == 'dir':
            return os.path.isdir(data)
        elif data_type == 'file':
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
            log.error("{} not valid. {} extension expected".format(data, ext))
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
            datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            log.error("%s not in valid format of YYYY-mm-dd HH:MM", data)
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
            log.error("TIMESTAMP not in met data.")
            return False
        unit_names = df.iloc[1].to_list()
        if 'TS' not in unit_names:
            log.error("TIMESTAMP expected unit TS not found in data")
            return False
        min_avg = df.iloc[2].to_list()
        if not ('Min' in min_avg or 'Avg' in min_avg):
            log.error("'Min' or 'Avg' keywords expected in third row of met data")
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
        site_name_col = df.filter(regex=re.compile('^name|site name', re.IGNORECASE)).columns.to_list()
        if not site_name_col:
            log.error("Site name not in Soils key")
            return False
        # check if required columns are present. the required cols are given below
        req_cols = ['Datalogger/met water variable name', 'Datalogger/met temperature variable name',
                    'EddyPro temperature variable name', 'EddyPro water variable name']
        # get column names matching datalogger / met tower
        met_cols = df.filter(regex=re.compile("datalogger|met tower", re.IGNORECASE)).columns.to_list()
        # get column names matching eddypro
        eddypro_cols = df.filter(regex=re.compile("^eddypro", re.IGNORECASE)).columns.to_list()
        # get column names matching pyfluxpro
        pyfluxpro_cols = df.filter(regex=re.compile("^pyfluxpro", re.IGNORECASE)).columns.to_list()
        if not met_cols or not eddypro_cols or not pyfluxpro_cols:
            print("Check for required columns in soils key: ", end='')
            print("Datalogger/met water variable name, Datalogger/met temperature variable name, "
                  "EddyPro temperature variable name, EddyPro water variable name, "
                  "PyFluxPro water variable name, PyFluxPro temperature variable name")
            return False

        # remove variable columns that have 'old' in the name
        old_pattern = re.compile(r'old', re.IGNORECASE)
        met_cols = list(filter(lambda x: not old_pattern.search(x), met_cols))
        eddypro_cols = list(filter(lambda x: not old_pattern.search(x), eddypro_cols))
        pyfluxpro_cols = list(filter(lambda x: not old_pattern.search(x), pyfluxpro_cols))

        # get temp and water variable columns from the above column list
        temp_pattern = re.compile(r'temperature|temp', re.IGNORECASE)
        water_pattern = re.compile(r"water|moisture", re.IGNORECASE)
        met_temp_col = list(filter(temp_pattern.search, met_cols))
        met_water_col = list(filter(water_pattern.search, met_cols))
        if not met_water_col or not met_temp_col:
            print("Check for required columns in soils key: ", end='')
            print("Datalogger/met water variable name, Datalogger/met temperature variable name")
            return False
        eddypro_temp_col = list(filter(temp_pattern.search, eddypro_cols))
        eddypro_water_col = list(filter(water_pattern.search, eddypro_cols))
        if not eddypro_water_col or not eddypro_temp_col:
            print("Check for required columns in soils key: ", end='')
            print("EddyPro temperature variable name, EddyPro water variable name")
            return False
        pyfluxpro_temp_col = list(filter(temp_pattern.search, pyfluxpro_cols))
        pyfluxpro_water_col = list(filter(water_pattern.search, pyfluxpro_cols))
        if not pyfluxpro_water_col or not pyfluxpro_temp_col:
            print("Check for required columns in soils key: ", end='')
            print("PyFluxPro water variable name, PyFluxPro temperature variable name")
            return False
        # all validations done
        return True

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
        date_col = df.filter(regex=re.compile("^date", re.IGNORECASE)).columns.to_list()
        time_col = df.filter(regex=re.compile("^time", re.IGNORECASE)).columns.to_list()
        if not date_col:
            log.error("Date column not present in EddyPro full output sheet")
            return False
        if not time_col:
            log.error("Time column not present in EddyPro full output sheet")
            return False
        sonic_temperature_col = df.filter(regex=re.compile("^sonic_temperature", re.IGNORECASE)).columns.to_list()
        if not sonic_temperature_col:
            log.error("Sonic temperature column not present in EddyPro full output sheet")
            return False
        air_pressure_col = df.filter(regex=re.compile("^air_pressure", re.IGNORECASE)).columns.to_list()
        if not air_pressure_col:
            log.error("Air pressure column not present in EddyPro full output sheet")
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
        # check if required columns are present. required columns are given below
        req_cols = ['Original variable name', 'Ameriflux variable name', 'Units after formatting']
        df_cols = df.columns.to_list()
        original_pattern = re.compile(r'^original', re.IGNORECASE)
        ameriflux_pattern = re.compile(r'^ameriflux', re.IGNORECASE)
        units_pattern = re.compile(r'^units', re.IGNORECASE)
        original_col = list(filter(original_pattern.search, df_cols))
        ameriflux_col = list(filter(ameriflux_pattern.search, df_cols))
        units_col = list(filter(units_pattern.search, df_cols))
        if original_col and ameriflux_col and units_col:
            # all required columns are present
            return True
        else:
            log.error("Check for required columns in Amerilfux-Mainstem-Key: ", end='')
            log.error("Original variable name, Ameriflux variable name, Units after formatting")
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
            log.error("Ameriflux label column not present in L1 Erroring variables sheet")
            return False
        if not pyfluxpro_col:
            log.error("Pyfluxpro label column not present in L1 Erroring variables sheet")
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
            log.error("Incorrect format in Level section")
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
                        log.error("Incorrect format in L1 Variables section")
                        return False
                else:
                    log.error("Incorrect format in L1 Global section")
                    return False
            else:
                log.error("Incorrect format in L1 Files section")
                return False
        else:
            log.error("Undefined L1 Files and Global section")
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
            if line_split[0].lower().strip() == 'level' and line_split[1].strip() == 'L1':
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
            if line.strip().lower().startswith('file_path'):
                file_path_flag = True  # found file_path line
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4:
                    # number of spaces is not as expected
                    return False
            if line.strip().lower().startswith('out_filename'):
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
            if line.strip().lower().startswith('acknowledgement'):
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
            if line.strip().lower().startswith(units_pattern):
                units_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if line.strip().lower().startswith(long_name_pattern):
                long_name_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if line.strip().lower().startswith(name_pattern):
                name_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            if line.strip().lower().startswith(sheet_pattern):
                sheet_flag = True
                if L1Validation.check_space(line.split('=')[0].rstrip()) != 4 * 3:
                    return False
            # test if all flag values are true
            flags = [var_flag, xl_flag, attr_flag, units_flag, long_name_flag, name_flag, sheet_flag]
            if all(flags) and var_count == 1:
                # all flag values are true, then break out of for loop
                return True
            elif var_count > 1:
                log.error("Check first variable in Variables section")
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
    VAR_PATTERN = '^ {4}\\[\\[[a-zA-Z0-9_]+\\]\\]\n$'  # variable name pattern
    DEPENDENCYCHECK_PATTERN = '^ {8}\\[\\[\\[DependencyCheck\\]\\]\\]\n$'
    EXCLUDEDATES_PATTERN = '^ {8}\\[\\[\\[ExcludeDates\\]\\]\\]\n$'
    RANGECHECK_PATTERN = '^ {8}\\[\\[\\[RangeCheck\\]\\]\\]\n$'
    SOURCE_PATTERN = '^ {12}source'  # to match the source in DependencyCheck
    LOWER_PATTERN = '^ {12}lower'  # to match the lower in RangeCheck
    UPPER_PATTERN = '^ {12}upper'  # to match the lower in RangeCheck

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
            log.error("Incorrect format in Level section")
            return False
        # check Variables section
        try:
            variables_line_index = lines.index('[Variables]\n')
        except ValueError:
            log.error("ERROR : No [Variables] present in L2.txt.")
            return False
        try:
            plots_line_index = lines.index('[Plots]\n')
        except ValueError:
            log.error("WARNING: no [Plots] present in L2.txt")
            plots_line_index = None
        if variables_line_index and plots_line_index:
            if L2Validation.check_variables_line(lines[variables_line_index + 1:plots_line_index]):
                return True
            else:
                log.error("Incorrect format in L2 Variables section")
                return False
        elif variables_line_index:
            if L2Validation.check_variables_line(lines[variables_line_index + 1:]):
                return True
            else:
                log.error("Undefined L2 Variables and Plots sections")
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
            if line_split[0].lower().strip() == 'level' and line_split[1].strip() == 'L2':
                return True
        return False

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
        var_start_end = L2Validation.get_variables_index(lines, var_pattern)
        # check if excludedates, rangecheck and dependencycheck follow the expected format
        for start, end in var_start_end:
            is_success = L2Validation.check_var_sections(lines[start:end], dependencycheck_pattern, rangecheck_pattern,
                                                         excludedates_pattern, source_pattern,
                                                         lower_pattern, upper_pattern)
            if not is_success:
                return False
        # all validations done
        return True

    @staticmethod
    def get_variables_index(text, var_pattern):
        """
            Get all variables and start and end index for each variable from the pyfluxpro control file

            Args:
                text (list): List with all variable lines from L2.txt
                var_pattern (str): Regex pattern of variable names
            Returns:
                var_start_end (list): List of tuple, the starting and ending index for each variable
        """
        var_indexes = [i for i, item in enumerate(text) if re.match(var_pattern, item)]
        var_start_end = []
        for i in range(len(var_indexes)-1):
            start_ind = var_indexes[i]
            end_ind = var_indexes[i+1]
            var_start_end.append((start_ind, end_ind))
        return var_start_end

    @staticmethod
    def check_var_sections(lines, dependencycheck_pattern, rangecheck_pattern, excludedates_pattern, source_pattern,
                           lower_pattern, upper_pattern):
        """
        Method to validate each sections of a Variable.
        Method checks if excludedates, rangecheck and dependencycheck follow the expected format
        Check if rangecheck has lower and upper lines. Check if source line exists for DependencyCheck
        Check if excludedates has from and to dates that are comma separated and if the dates are valid
        Args:
            lines (list): Lines of a variable from L2.txt
            dependencycheck_pattern (str): Regex pattern of dependency check section
            rangecheck_pattern (str): Regex pattern of range check section
            excludedates_pattern (str): Regex pattern of exclude dates section
            source_pattern (str): Regex pattern for source line in Dependency check section
            lower_pattern (str): Regex pattern for lower line in Range check section
            upper_pattern (str): Regex pattern for upper line in Range check section
        Returns:
            (bool): Returns True if all section validations are complete, else returns False
        """
        depcheck_line_index = [i for i, item in enumerate(lines) if re.match(dependencycheck_pattern, item)]
        rangecheck_line_index = [i for i, item in enumerate(lines) if re.match(rangecheck_pattern, item)]
        excludedates_line_index = [i for i, item in enumerate(lines) if re.match(excludedates_pattern, item)]
        # get value from list
        if depcheck_line_index:
            depcheck_line_index = depcheck_line_index[0]
        else:
            depcheck_line_index = None
        if rangecheck_line_index:
            rangecheck_line_index = rangecheck_line_index[0]
        else:
            rangecheck_line_index = None
        if excludedates_line_index:
            excludedates_line_index = excludedates_line_index[0]
        else:
            excludedates_line_index = None
        section_index = {'excludedates': excludedates_line_index, 'rangecheck': rangecheck_line_index,
                         'depcheck': depcheck_line_index}
        # exclude dates section can have arbitary number of lines.
        # get the ending line index for exclude dates section by sorting other section indexes
        section_index = dict(sorted(section_index.items(), key=lambda item: (item[1] is None, item[1])))
        excludedates_section_index = list(section_index.keys()).index('excludedates')
        if excludedates_section_index == 2:
            # exclude dates section is the last section. the end index will be the ending index of the variable section
            excludedates_end_index = len(lines) - 1
        else:
            # exclude dates section is not the last. end index will be the starting index of the next section.
            excludedates_end_index = list(section_index.values())[excludedates_section_index + 1]

        depcheck_flag, rangecheck_flag, excludedates_flag = False, False, False

        # validate dependency check section
        if depcheck_line_index:
            # dependency section exists
            if re.match(source_pattern, lines[depcheck_line_index+1]):
                depcheck_flag = True
            else:
                log.error("Check Dependency Check format in line %s", str(lines[depcheck_line_index+1]).rstrip())
                depcheck_flag = False

        # validate rangecheck section
        if rangecheck_line_index:
            # check if the first line or second line matches the lower pattern
            if re.match(lower_pattern, lines[rangecheck_line_index+1]):
                lower_line = lines[rangecheck_line_index + 1]
            elif re.match(lower_pattern, lines[rangecheck_line_index+2]):
                lower_line = lines[rangecheck_line_index + 2]
            # check if the first line or second line matches the upper pattern
            if re.match(upper_pattern, lines[rangecheck_line_index+2]):
                upper_line = lines[rangecheck_line_index + 2]
            elif re.match(upper_pattern, lines[rangecheck_line_index+1]):
                upper_line = lines[rangecheck_line_index + 1]
            lower_items = lower_line.strip().split('=')[1].split(',')
            upper_items = upper_line.strip().split('=')[1].split(',')
            if lower_items and upper_items:
                # NOTES 21
                lower_items_num = len(lower_items)
                upper_items_num = len(upper_items)
                if (lower_items_num == 1 or lower_items_num == 12) and (upper_items_num == 1 or upper_items_num == 12):
                    rangecheck_flag = True
                else:
                    print("Check number of items in lower and upper ranges in line", lines[rangecheck_line_index])
                    rangecheck_flag = False
            else:
                log.error("Check Range Check format in line %s", str(lines[rangecheck_line_index]).rstrip())
                rangecheck_flag = False

        # validate exclude dates section
        if excludedates_line_index:
            # if ExcludeDates section is present, check if the dates are valid
            # first line is ExcludeDates. start iteration from the next line onwards
            for line in lines[excludedates_line_index+1:excludedates_end_index]:
                date_line = line.split('=')[1]
                dates = date_line.strip().split(',')
                start_date, end_date = dates[0].strip(), dates[1].strip()
                if DataValidation.datetime_validation(start_date) and DataValidation.datetime_validation(end_date) and \
                        pd.to_datetime(end_date) > pd.to_datetime(start_date):
                    excludedates_flag = True
                else:
                    excludedates_flag = False
                    log.error("Check dateformat in line %s", line.strip())
                    break

        if depcheck_line_index and (not depcheck_flag):
            log.error("Check DependencyCheck section for variable {}".format(lines[0].strip()))
            return False
        elif rangecheck_line_index and (not rangecheck_flag):
            log.error("Check RangeCheck section for variable {}".format(lines[0].strip()))
            return False
        elif excludedates_line_index and (not excludedates_flag):
            log.error("Check ExcludeDates section for variable {}".format(lines[0].strip()))
            return False
        else:
            # all validations done
            return True
