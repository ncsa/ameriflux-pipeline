# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/
import subprocess
import os

OUT_TEMP_PROJ_FILE = os.path.join(os.getcwd(), 'templates', 'out_proj.eddypro')
IN_TEMP_PROJ_FILE = os.path.join(os.getcwd(), 'templates', 'test-v2.eddypro')

def run_eddypro(eddypro_loc="", file_name="", project_title="", file_prototype="", proj_file="",
                dyn_metadata_file="", out_path="", biom_file="", data_path=""):

    # manipulate project file from the template project file
    tmp_proj_list = create_tmp_proj_file(file_name=file_name, project_title=project_title,
                                         file_prototype=file_prototype,
                                         proj_file=proj_file, dyn_metadata_file=dyn_metadata_file, out_path=out_path,
                                         biom_file=biom_file, data_path=data_path)

    # save temporary project file
    save_string_list_to_file(tmp_proj_list)

    try:
        subprocess.run([eddypro_loc, OUT_TEMP_PROJ_FILE], shell=True)
    except Exception:
        raise Exception("Running EddyPro failed.")

    # remove temporary project file


def create_tmp_proj_file(file_name, project_title, file_prototype, proj_file, dyn_metadata_file,
                         out_path, biom_file, data_path):
    # read the template file
    temp_proj_file = open(IN_TEMP_PROJ_FILE, mode='r', encoding='utf-8')
    lines = temp_proj_file.readlines()
    temp_proj_file.close()
    out_proj_file_line_list = []

    try:
        for line in lines:
            # check if line starts with the given keyword
            words = line.split("=")

            # 'file_name'
            if words[0].lower() == 'file_name':
                if len(words[1]) > 0 and len(file_name) > 0:
                    line = 'file_name=' + file_name

            # 'proj_file'
            if words[0].lower() == 'proj_file':
                if len(words[1]) > 0 and len(proj_file) > 0:
                    line = 'proj_file=' + proj_file

            # 'dyn_metadata_file'
            if words[0].lower() == 'dyn_metadata_file':
                if len(words[1]) > 0 and len(dyn_metadata_file) > 0:
                    line = 'dyn_metadata_file=' + dyn_metadata_file

            # 'biom_file'
            if words[0].lower() == 'biom_file':
                if len(words[1]) > 0 and len(biom_file) > 0:
                    line = 'biom_file=' + biom_file

            # 'data_path'
            if words[0].lower() == 'data_path':
                if len(words[1]) > 0 and len(data_path) > 0:
                    line = 'data_path=' + data_path

            # 'project_title'
            if words[0].lower() == 'project_title':
                if len(words[1]) > 0 and len(project_title) > 0:
                    line = 'project_title=' + project_title

            # 'file_prototype'
            if words[0].lower() == 'file_prototype':
                if len(words[1]) > 0 and len(file_prototype) > 0:
                    line = 'file_prototype=' + file_prototype

            # 'out_path'
            if words[0].lower() == 'out_path':
                if len(words[1]) > 0 and len(out_path) > 0:
                    line = 'out_path=' + out_path

            out_proj_file_line_list.append(line.strip())

    except Exception:
        raise Exception("Manipulating template project file failed.")

    return out_proj_file_line_list


def save_string_list_to_file(in_list, outfile=OUT_TEMP_PROJ_FILE):
    try:
        out_proj_file = open(outfile, "w")
        for line in in_list:
            out_proj_file.write(line + "\n")
        out_proj_file.close()
    except Exception:
        raise Exception("Failed to create temporary project file")


if __name__ == '__main__':
    eddypro_loc = "C:\\Program Files\\LI-COR\\EddyPro-7.0.7\\bin\\eddypro_rp.exe"
    # proj_file=C:/Users/Bethany/Desktop/EddyPro_Practice/2020-10-08T130000_Sorghum-00137.metadata
    # dyn_metadata_file=C:/Users/Bethany/Desktop/EddyPro_Practice/Sorghum_2020_dynamic_metadata.csv
    # out_path=C:/Users/Bethany/Desktop/EddyPro_Practice/Output_OctDec
    # biom_file=C:/Users/Bethany/Desktop/EddyPro_Practice/Sorghum_2020_Met_Data_for_EddyPro.csv
    # data_path=C:/Users/Bethany/Desktop/EddyPro_Practice/GHGFiles/Files_OctDec
    file_name = "C:/Users/ywkim/Documents/Ameriflux/test-v2.eddypro"
    project_title = "test_sample_data"
    file_prototype = "yyyy-mm-ddTHHMM??_AIU-0288.ghg"
    proj_file = ""
    dyn_metadata_file = ""
    out_path = "C:/Users/ywkim/Documents/Ameriflux/Data/ghg_sample_data_2/GHG_Raw_Data_withBiomet_processed"
    data_path = "C:/Users/ywkim/Documents/Ameriflux/Data/ghg_sample_data_2/GHG_Raw_Data_withBiomet"
    run_eddypro(eddypro_loc=eddypro_loc, file_name=file_name, project_title=project_title,
                file_prototype=file_prototype, proj_file=proj_file, dyn_metadata_file=dyn_metadata_file,
                out_path=out_path, data_path=data_path)
