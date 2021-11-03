# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import ameriflux_pipeline.runeddypro as runeddypro


def test_run_eddypro():
    eddypro_loc = "/Applications/eddypro.app/Contents/MacOS/bin/eddypro_rp"
    file_name = "/Users/minum/Documents/NCSA/AmeriFlux/Ameriflux_Github/ameriflux-pipeline/ameriflux_pipeline/templates/EddyPro_Run_Template.eddypro"
    project_title = "Project Title"
    project_id = "Project ID"
    file_prototype = "yyyy-mm-ddTHHMM??_Sorghum-00137.ghg"  # yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
    proj_file = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/Raw Jan-Mar 2021 GHG Files/2021-01-01T000000_Sorghum-00137/2021-01-01T000000_Sorghum-00137.metadata"  # 2021-01-01T000000_Sorghum-00137.metadata
    dyn_metadata_file = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/Sorghum_2021_dynamic_metadata.csv"  # Sorghum_2021_dynamic_metadata.csv
    out_path = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/"
    data_path = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/Raw Jan-Mar 2021 GHG Files"  # Raw_Jan-Mar_2021_GHG_Files
    biom_file = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/Met_Data_for_EddyPro.csv"  # FLUXSB_EC_JanMar2021_output_eddypro.csv
    ex_file = "/Users/minum/Documents/NCSA/AmeriFlux/Files to run EddyPro GUI/eddypro_Efarm_Sorghum_Reanalysis_2020_fluxnet_2021-10-26T101711_adv.csv"
    runeddypro.run_eddypro(eddypro_loc=eddypro_loc, file_name=file_name, project_id=project_id,
                           project_title=project_title, file_prototype=file_prototype, proj_file=proj_file,
                           dyn_metadata_file=dyn_metadata_file, out_path=out_path, data_path=data_path,
                           biom_file=biom_file, ex_file=ex_file)

if __name__ == '__main__':
    test_run_eddypro()

