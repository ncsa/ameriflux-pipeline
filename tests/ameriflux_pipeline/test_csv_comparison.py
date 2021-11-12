# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import pandas as pd


def compare_eddypro_outputs(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # make two frames with same rows
    df1 = df1.iloc[0:15]
    df2 = df2.iloc[0:15]

    print(df1.compare(df2))


if __name__ == '__main__':
    file1 = "C:\\Users\\ywkim\\Documents\\Ameriflux\\Data\\minu_test\\Test_output\\" \
            "eddypro_Efarm_Sorghum_Reanalysis_2020_full_output_2021-10-26T101711_adv_processed.csv"
    file2 = "C:\\Users\\ywkim\\Documents\\Ameriflux\\Data\\bethany_test\\EddyPro_ManualOutput_20201_Jan_Mar\\Jan\\" \
            "eddypro_UIUC_Sorghum_2021_Jan_full_output_2021-04-14T114311_adv.csv"

    compare_eddypro_outputs(file1, file2)
