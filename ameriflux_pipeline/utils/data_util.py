# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

def write_data(df, output_data):
    """
    Write the dataframe to csv file
    :param df: input dataframe to be written to csv file
           output_data : filename to write data
    :return: None
    """
    df.to_csv(output_data, index=False)
    pass
