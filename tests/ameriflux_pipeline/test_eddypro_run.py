# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os
import ameriflux_pipeline.runeddypro as runeddypro


def test_run_eddypro():
    OUT_TEMP_PROJ_FILE = os.path.join('templates', 'out_proj.eddypro')
    tmp_proj_file = "C:\\Workspace-ameriflux\\ameriflux-pipeline\\ameriflux_pipeline\\templates\\EddyPro_Run_Template.eddypro"
    eddypro_loc = "C:\\Program Files\\LI-COR\\EddyPro-7.0.7\\bin\\eddypro_rp.exe"
    file_name = "C:/Users/ywkim/Documents/Ameriflux/test-v2.eddypro"
    project_title = "EFarm_Sorghum_Reanalysis_2020"
    project_id = "Efarm_Sorghum_Reanalysis_2020"
    file_prototype = "yyyy-mm-ddTHHMM??_Sorghum-00137.ghg"
    proj_file = "C:/Users/ywkim/Documents/Ameriflux/Data/minu_test/2021-01-01T000000_Sorghum-00137.metadata"
    dyn_metadata_file = "C:/Users/ywkim/Documents/Ameriflux/Data/minu_test/Sorghum_2021_dynamic_metadata.csv"
    out_path = "C:/Users/ywkim/Documents/Ameriflux/Data/minu_test/Test_output"
    data_path = "C:/Users/ywkim/Documents/Ameriflux/Data/minu_test/Raw_Jan-Mar_2021_GHG_Files"
    biom_file="C:/Workspace-ameriflux/ameriflux-pipeline/tests/data/FLUXSB_EC_JanMar2021_output_eddypro.csv"
    ex_file = "C:/Users/ywkim/Documents/Ameriflux/Data/minu_test/Test output/eddypro_Efarm_Sorghum_Reanalysis_2020_fluxnet_2021-10-26T101711_adv.csv"

    runeddypro.run_eddypro(eddypro_loc=eddypro_loc, tmp_proj_file=tmp_proj_file, file_name=file_name, project_id=project_id,
                           project_title=project_title, file_prototype=file_prototype, proj_file=proj_file,
                           dyn_metadata_file=dyn_metadata_file, out_path=out_path, data_path=data_path,
                           biom_file=biom_file, ex_file=ex_file)

if __name__ == '__main__':
    test_run_eddypro()

