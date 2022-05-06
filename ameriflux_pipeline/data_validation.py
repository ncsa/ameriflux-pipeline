# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import validators
from validators import ValidationFailure
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
            print(data, "not floating point")
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
        Method to check if both inputs are equal
        Returns True if equal, else returns False
        Args:
            data1: Input data 1
            data2: Input data 2
        Returns:
            (bool): True if float, else False
        """
        return data1 == data2


    @staticmethod
    def url_validation(data):
        """
        Method to check if data is a url
        Returns True if valid url, else returns False
        Args:
            data (string): Input data
        Returns:
            (bool): True if url, else False
        """
        is_url = validators.url(data)
        if isinstance(is_url, ValidationFailure):
            print(data, "not valid url")
            return False
        return True


    @staticmethod
    def domain_validation(data):
        """
        Method to check if data is a domain or hostname
        Returns True if valid, else returns False
        Args:
            data (string): Input data
        Returns:
            (bool): True if valid, else False
        """
        is_domain = validators.domain(data)
        if isinstance(is_domain, ValidationFailure):
            print(data, "not valid domain")
            return False
        return True


    @staticmethod
    def ip_validation(data):
        """
        Method to check if data is a valid ip address
        Returns True if valid, else returns False
        Args:
            data (string): Input data
        Returns:
            (bool): True if valid, else False
        """
        try:
            is_ip = ipaddress.ip_address(data)
        except ValueError:
            print(data, "not valid ip")
            return False
        return True


    @staticmethod
    def path_validation(data, type):
        """
        Method to check if both the data path is same as type
        Returns True if same, else returns False
        Args:
            data (str): Input data path
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
            data (str): Input file path with file extension
            ext (str): Expected file extension
        Returns:
            (bool): True if file extension is same as expected, else False
        """
        # separate filename and extension
        filename, extension = os.path.splitext(data)
        if extension.lower() == ext.lower():
            return True
        else:
            print(data, "not valid extension")
            return False


    @staticmethod
    def is_empty_dir(data):
        """
        Method to check if both the directory contains files
        Returns False if empty, else returns True
        Args:
            data (str): Input data path
        Returns:
            (bool): True if directory is not empty, else False
        """
        if not os.listdir(data):
            return False
        else:
            return True

