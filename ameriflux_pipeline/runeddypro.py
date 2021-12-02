# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/
import subprocess
import os
import shutil


class RunEddypro():
    """
    This is a class for running EddyPro in the pipeline
    """

    @staticmethod
    def run_eddypro(eddypro_bin_loc="", file_name="", project_title="", project_id="", file_prototype="",
                    proj_file="", dyn_metadata_file="", out_path="", data_path="", biom_file=""):
        """
            Run EddyPro headless using the given parameters

            Args:
                eddypro_bin_loc (str): A path for the eddypro bin directory location
                file_name (str): A file path for eddypro project filename
                project_title (str): A title for the project
                project_id (str): An ID for the project
                file_prototype (str): A file format, such as yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
                proj_file (str): A file path for metadata. This could be obtained by unzipping ghg file
                dyn_metadata_file (str): A file path for dynamic metadata file
                out_path (str): A directory path for output data to be stored
                data_path(str): A directory path for input data, such as ghg files
                biom_file (str): A file path for master biomet data
            Returns:
                None
        """
        # create out temp project file
        outfile = os.path.join(os.path.dirname(os.path.abspath(file_name)), "templates.eddypro")

        # manipulate project file from the template project file
        tmp_proj_list = RunEddypro.create_tmp_proj_file(
            file_name=file_name, project_title=project_title, project_id=project_id, file_prototype=file_prototype,
            proj_file=proj_file, dyn_metadata_file=dyn_metadata_file, out_path=out_path, data_path=data_path,
            biom_file=biom_file, outfile=outfile)

        # clean up the eddypro output folder
        print("All the contents in the", out_path, "will be removed.")
        for filename in os.listdir(out_path):
            file_path = os.path.join(out_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        # save temporary project file
        RunEddypro.save_string_list_to_file(tmp_proj_list, outfile)
        print("temporary project file created")

        # copy eddypro bin folder content to working folder.
        # This is to avoid possible unzip error of ghz file that eddypro_rp has
        current_dir = os.getcwd()
        bin_list = os.listdir(eddypro_bin_loc)

        # copy eddypro bin files
        for bin_file in bin_list:
            src_file = os.path.join(eddypro_bin_loc, bin_file)
            des_file = os.path.join(current_dir, bin_file)
            try:
                shutil.copyfile(src_file, des_file)  # does not copy empty directories
            except Exception:
                print(bin_file, "already exists in the working directory.")
        print("copied temporary eddypro bin files")

        try:
            subprocess.run(["./eddypro_rp -s mac -e", os.path.dirname(os.path.abspath(file_name)), outfile], shell=True)
        except Exception:
            raise Exception("Running EddyPro failed.")

        # remove temporary project file
        print("removed temporary project file")
        os.remove(outfile)

        # remove temporary bin file
        for bin_file in bin_list:
            os.remove(os.path.join(current_dir, bin_file))
        print("removed temporary eddypro bin files")

    @staticmethod
    def create_tmp_proj_file(file_name, project_title,
                             project_id, file_prototype,
                             proj_file, dyn_metadata_file,
                             out_path, data_path,
                             biom_file, outfile):

        """
            Create temporary project file for running the EddyPro

            Args:
                file_name (str): A file path for eddypro project filename
                project_title (str): A title for the project
                project_id (str): An ID for the project
                file_prototype (str): A file format, such as yyyy-mm-ddTHHMM??_Sorghum-00137.ghg
                proj_file (str): A file path for metadata. This could be obtained by unzipping ghg file
                dyn_metadata_file (str): A file path for dynamic metadata file
                out_path (str): A directory path for output data to be stored
                data_path(str): A directory path for input data, such as ghg files
                biom_file (str): A file path for master biomet data
                outfile (str): A file path for output temporary eddypro project file
            Returns:
                None
        """
        # read the template file
        temp_proj_file = open(file_name, mode='r', encoding='utf-8')
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
                        line = 'file_name=' + outfile

                # 'project_title'
                if words[0].lower() == 'project_title':
                    if len(words[1]) > 0 and len(project_title) > 0:
                        line = 'project_title=' + project_title

                # 'project_id'
                if words[0].lower() == 'project_id':
                    if len(words[1]) > 0 and len(project_id) > 0:
                        line = 'project_id=' + project_id

                # 'file_prototype'
                if words[0].lower() == 'file_prototype':
                    if len(words[1]) > 0 and len(file_prototype) > 0:
                        line = 'file_prototype=' + file_prototype

                # 'proj_file'
                if words[0].lower() == 'proj_file':
                    if len(words[1]) > 0 and len(proj_file) > 0:
                        line = 'proj_file=' + proj_file

                # 'dyn_metadata_file'
                if words[0].lower() == 'dyn_metadata_file':
                    if len(words[1]) > 0 and len(dyn_metadata_file) > 0:
                        line = 'dyn_metadata_file=' + dyn_metadata_file

                # 'out_path'
                if words[0].lower() == 'out_path':
                    if len(words[1]) > 0 and len(out_path) > 0:
                        line = 'out_path=' + out_path

                # 'data_path'
                if words[0].lower() == 'data_path':
                    if len(words[1]) > 0 and len(data_path) > 0:
                        line = 'data_path=' + data_path

                # 'biom_file'
                if words[0].lower() == 'biom_file':
                    if len(words[1]) > 0 and len(biom_file) > 0:
                        line = 'biom_file=' + biom_file

                out_proj_file_line_list.append(line.strip())

        except Exception:
            raise Exception("Manipulating template project file failed.")

        return out_proj_file_line_list

    def save_string_list_to_file(in_list, outfile):
        """
            Save list with string to a file

            Args:
                in_list (list): List of the strings that are the eddypro project file elements
                outfile (str): A file path of the output file

            Returns:
                None
        """
        try:
            out_proj_file = open(outfile, "w")
            for line in in_list:
                out_proj_file.write(line + "\n")
            out_proj_file.close()
        except Exception:
            raise Exception("Failed to create temporary project file")