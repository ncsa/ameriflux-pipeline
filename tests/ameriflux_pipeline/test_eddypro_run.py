# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

from ameriflux_pipeline.runeddypro import RunEddypro


def test_run_eddypro():
    eddypro_bin_loc = "/path/to/LI-COR//EddyPro-7.0.7/bin/"  # directory path to eddypro bin folder
    file_name = "/should/be/same/as/tmp/proj_file"
    project_title = "Project Title"
    project_id = "Project ID"
    file_prototype = "file_prototype"  # yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
    proj_file = "/path/to/metadata"  # 2021-01-01T000000_Sorghum-00137.metadata
    dyn_metadata_file = "/path/to/dyn_metadata"  # Sorghum_2021_dynamic_metadata.csv
    out_path = "/path/to/output"
    data_path = "/path/to/GHG_files"  # Raw_Jan-Mar_2021_GHG_Files
    biom_file = "/path/to/biom_file"  # FLUXSB_EC_JanMar2021_output_eddypro.csv
    ex_file = "/path/to/ex_file"  # eddypro_Efarm_Sorghum_Reanalysis_2020_fluxnet_2021-10-26T101711_adv.csv

    RunEddypro.run_eddypro(eddypro_bin_loc=eddypro_bin_loc, file_name=file_name, project_id=project_id,
                           project_title=project_title, file_prototype=file_prototype, proj_file=proj_file,
                           dyn_metadata_file=dyn_metadata_file, out_path=out_path, data_path=data_path,
                           biom_file=biom_file)


if __name__ == '__main__':
    test_run_eddypro()
