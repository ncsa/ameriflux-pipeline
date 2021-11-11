# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

def write_data(df, output_data):
    """Write the dataframe to csv file
        Args:
            df (object): Pandas DataFrame object
            output_data_path (str): File path to save output data
        Returns:
            None
    """
    print("Write data to file ", output_data)
    df.to_csv(output_data, index=False)
