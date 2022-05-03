# Copyright (c) 2022 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/


class Validation:
    '''
    Class to implement data validation
    '''
    # TODO: add methods for date validation, string input validation.

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
    def path_validation(path, type):
        """
        Method to check if both inputs are equal
        Returns True if equal, else returns False
        Args:
            data1: Input data 1
            data2: Input data 2
        Returns:
            (bool): True if float, else False
        """