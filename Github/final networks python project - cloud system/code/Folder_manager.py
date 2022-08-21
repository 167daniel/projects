__author__ = 'daniel'

from uuid import uuid4
from Utils import *
from shutil import rmtree
from distutils.dir_util import copy_tree
import zlib, os, errno


# while reading this code it is important to understand open() file modes
# also it is important to understand that to edit a filein the middle of it we have to write it all over again
# main sync reefers to a guid generated folder

# for every synchronization folder being created\loaded an object of type Folder is being created too
class Folder:
    def __init__(self, name, owner, guid=None, shared_users=[]):
        self.name = name
        self.owner = owner
        self.shared_users = shared_users

        # if the folder is just being created and not loaded
        if guid is None:
            self.guid = str(uuid4())  # calculate a guid

            # write to folders file the new synchronization folder
            with open("Folders", "a+") as f:
                f.write(str(self.guid) + ">" + self.name + ">" + self.owner + ">" + list_to_string(
                    self.shared_users) + "\n")

        # the folder is being created for the first time
        else:
            self.guid = guid

        # if the synchronization folder  dosent exist in path create it
        if not os.path.exists(r".\users_folders\%s" % self.guid):
            os.makedirs(r".\users_folders\%s" % self.guid)

    # changes the virtual name of the main sync folder
    def change_name(self, new_name):
        self.name = new_name


# --------------------------------------------------------------------------------------------->>>
# --------------------------------------------------------------------------------------------->>>

# this class takes care of everything being relarted to synchronizing folders and files
class Folder_manager:
    def __init__(self):
        self.folders = []
        self._load_folders()  # load the folders that alraedy exist to folders virtual list

    # --------------------------------------------------------------------------------------------->>>
    # load the folders that alraedy exist to folders virtual list
    def _load_folders(self):
        if os.path.exists("Folders"):
            with open("Folders", "r+") as f:  # does not trancuates
                data = f.read()

                # a line present a folder, load every folder
                for line in data.splitlines():
                    guid, name, owner, shared_users = line.split(">")
                    self.folders.append(Folder(name, owner, guid, string_to_list(shared_users)))

        # the system has not created yet the directory users_folders nor the folders file does not exist yet
        else:
            os.makedirs(".\\users_folders")

            # the file path does not exists and it will be created
            open(".\\Folders", "w+").close()

    # --------------------------------------------------------------------------------------------->>>
    # this function receives the name of a file and its owner as parameters and returns the releveant folder accordingly
    def _get_folder_by_owner(self, virtual_name, owner):
        for folder in self.folders:
            if folder.name == virtual_name and folder.owner == owner:
                return folder
        # this owner owns no folders
        return None

    # --------------------------------------------------------------------------------------------->>>
    # this function returns all the folders that belongs to the owner in a list
    def _get_folders_list_by_owner(self, owner):
        list_of_folders = []
        for folder in self.folders:
            if folder.owner == owner:
                list_of_folders.append(folder)

        return list_of_folders

    # --------------------------------------------------------------------------------------------->>>

    # the client has created a new folder or file on his computer as a result the server has to update itself
    # this function creates a new folder or file on the server according to the path and owner it recieves
    def create_folder_or_file(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        path, owner, new_name, isfile = get_multiple_params(params, ["PATH", "USER_NAME", "NEW_NAME", "IS_FILE"])

        # isfile is a str representing a boolean and we turn it back into a real boolean
        isfile = str_to_bool(isfile)

        # rearrange the path nd the virtual name
        path, virtual_name = change_path(path, 0,
                                         return_popped_path=True)  # virtual name is the name of guid folder in folders file

        # if the folder being created is a main sync folder
        if virtual_name == "":
            virtual_name = new_name

        # in the path the main sync folder name is the virtual name. this virtual name has to be changed with the real guid name
        # for that we have to get the folder object so we could get the guid
        folder = self._get_folder_by_owner(virtual_name, owner)

        # if the folder being the created is a main sync folder
        # there is also a need to update the folders file deleting the file itself is not enough
        if not folder:
            return self._create_main_sync_folder(virtual_name, owner)

        # rearanging the path of the file\folder
        path = ".\users_folders\\" + folder.guid + "\\" + path

        # if path ends with "\\" they are erased
        path = check_path_end(path)

        # the folder being created is not a main sync folder and its just regular file or folder so there is no need to update the foleders file
        new_folder_path = path + "\\" + new_name  # now the path include the file\folder to be created
        if os.path.exists(new_folder_path):
            return build_response("CREATE", status="FAILED_ALREADY_EXISTS")

        # if were creating a file
        if isfile:
            open(new_folder_path, 'a').close()

        # else were creating a file
        else:
            os.makedirs(new_folder_path)
        return build_response("CREATE")

    # --------------------------------------------------------------------------------------------->>>

    # this function creates a new main sync folder and update the folders file accordingly
    def _create_main_sync_folder(self, name, owner):
        if os.path.exists(".\\users_folders"):
            with open("Folders", "r+") as f:  # open the file for reading and writing dose not trancuate the file
                data = f.read()
                for line in data.splitlines():
                    line = line.split(">")

                    # if the file already exists
                    if line[1] == name and line[2] == owner:
                        return build_response("CREATE", status="FAILED_ALREADY_EXISTS")

                self.folders.append(Folder(name, owner))  # create a new Folder object in folders list
                return build_response("CREATE")

    # --------------------------------------------------------------------------------------------->>>

    # this function returns a list of the all the main sync folders that belong to the spesific owner
    # or that the the owner is shared with. it returns the virtual name and not the guid name
    def _get_user_folders(self, user_name):
        list_to_return = []
        for folder in self.folders:
            if folder.owner == user_name:
                list_to_return.append(folder.name)
            elif user_name in folder.shared_users:  # check if owner is shared with the folder
                list_to_return.append("<" + folder.name)
        return list_to_return

    # --------------------------------------------------------------------------------------------->>>

    # the client has added a new file to the syncronization folder and now the server will sync himself with the server
    def upload_file(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        path, owner, file_data = get_multiple_params(params, ["PATH", "USER_NAME", "FILE_DATA"])

        # arrange the path and the virtual name
        path, virtual_name = change_path(path, 0, return_popped_path=True)
        folder = self._get_folder_by_owner(virtual_name, owner)

        # if folder is None
        if folder is None:
            build_response("UPLOAD_FILE", status="FAILED_NO_SYNC_FOLDER")

        path = ".\users_folders\\" + folder.guid + "\\" + path

        # try to decompress the file that is being synced
        try:
            file_data = zlib.decompress(file_data.decode("hex"))

        # the file is corrupted
        except:
            return build_response("UPLOAD_FILE", status="FAILED_FILE_DATA_CORRUPTED")

        # if the file path does not exists it will be created
        with open(path, "wb+") as f:
            f.write(file_data)
        return build_response("UPLOAD_FILE")

    # --------------------------------------------------------------------------------------------->>>

    # this function deletes a main sync flder and updates the folders file accordingly
    def _delete_main_sync_folder(self, folder):

        if os.path.isdir(".\\users_folders\\%s" % folder.guid):
            rmtree(".\\users_folders\\%s" % folder.guid)  # removes the folder and its content
            new_folder_data = ""
            with open("Folders", "r+") as f:  # open for reading and writing does not trancuate
                data = f.read()
                for line in data.splitlines():
                    line = line.split(">")

                    # if the folder is the folder being deleted dont add it back to the folders file
                    if line[1] == folder.name and line[2] == folder.owner:
                        continue
                    new_folder_data += ">".join(line) + "\n"

                f.seek(0)
                f.truncate()  # erase the file
                f.write(new_folder_data)  # rewrite the file

            self.folders.remove(folder)
            return build_response("DELETE")  # success
        return build_response("DELETE", status="FAILED_PATH_DOES_NOT_EXIST")

    # --------------------------------------------------------------------------------------------->>>

    # the client has deleted a file and now the server will do the same
    def delete_folder_or_file(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        path, owner = get_multiple_params(params, ["PATH", "USER_NAME"])

        # arrange the path and the virtual name
        path, virtual_name = change_path(path, 0, return_popped_path=True)
        folder = self._get_folder_by_owner(virtual_name, owner)
        path = ".\users_folders\\" + folder.guid + "\\" + path

        # if path ends with "\\" they are erased
        path = check_path_end(path)

        # if the folder being the deleted is a main sync folder
        # there is also a need to update the folders file deleting the file itself is not enough
        if len(path.split("\\")) == 3:
            return self._delete_main_sync_folder(folder)

        if os.path.isfile(path):
            os.remove(path)

        # else a folder is being deleted
        else:
            rmtree(path)
        return build_response("DELETE")

    # --------------------------------------------------------------------------------------------->>>

    # this function renames the folder or the file
    def rename_folder_or_file(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        path, owner, new_name = get_multiple_params(params, ["PATH", "USER_NAME", "NEW_NAME"])

        # arrange the path and the virtual name
        path, virtual_name = self._get_original_path_and_virtual_name(path, owner)

        # if path ends with "\\" they are erased
        path = check_path_end(path)

        # if the folder thats being changed is a main sync folder
        # the only thing to be updated is the folders file not the actual folder cause the guid stayes the same
        if len(path.split("\\")) == 3:
            return self._rename_main_sync_folder(virtual_name, owner, new_name)

        # the folder being changed is not a main sync folder and its just regular file or folder so there is no need to update the foleders file
        new_folder_path = change_path(path, len(path.split("\\")) - 1,
                                      new_name)  # rearrange the path so it contains the new name of the file\folder instead of its current name
        if os.path.isdir(path):
            copy_tree(path, new_folder_path)
            rmtree(path)
        else:
            os.rename(path, new_folder_path)
        return build_response("RENAME")

    # --------------------------------------------------------------------------------------------->>>

    # this function renames a main sync folder
    def _rename_main_sync_folder(self, virtual_name, owner, new_folder_name):

        # check that the new name dose not exist already
        if self._get_folder_by_owner(new_folder_name, owner) is not None:
            return build_response("RENAME", status="FAILED_FOLDER_NAME_ALREADY_ EXISTS")

        with open("Folders", "r+") as f:  # open the file for reading writing and reading does not trancuate the file
            data = f.read()
            new_folders_file = ""
            for line in data.splitlines():
                line = line.split(">")

                # if this folder is the folder to be renamed
                if line[1] == virtual_name and line[2] == owner:
                    line[1] = new_folder_name  # rename the folder

                new_folders_file += ">".join(line) + "\n"
            f.seek(0)
            f.truncate()  # erase the file
            f.write(new_folders_file)  # rewrite the file
        self.change_virtual_name(virtual_name, owner, new_folder_name)
        return build_response("RENAME")

    # --------------------------------------------------------------------------------------------->>>
    # this function changes the virtual name of a Folder
    def change_virtual_name(self, virtual_name, owner, new_folder_name):
        folder = self._get_folder_by_owner(virtual_name, owner)  # get the spesific Folder
        folder.change_name(new_folder_name)  # changes the virtual name of the Folder to new_folder_name

    # --------------------------------------------------------------------------------------------->>>
    # send a file to the client according to his request
    def download_file(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        path, owner = get_multiple_params(params, ["PATH", "USER_NAME"])

        # arrange the path and the virtual name
        path, virtual_name = self._get_original_path_and_virtual_name(path, owner)

        # if the file exists
        if os.path.isfile(path):
            with open(path, "rb") as f:  # open the file for reading does not truncates the file
                file_data = str(zlib.compress(f.read()).encode("hex"))  # reading the file and compresses it
            return build_response("DOWNLOAD", {"FILE": file_data})  # succeded

        # error the file does not exists
        return build_response("DOWNLOAD", status="FAILED_PATH_DOES_NOT_EXISTS")

    # --------------------------------------------------------------------------------------------->>>
    # this function rearranges the path
    def _get_original_path_and_virtual_name(self, path, owner):

        path, virtual_name = change_path(path, 0, return_popped_path=True)
        folder = self._get_folder_by_owner(virtual_name, owner)
        path = ".\users_folders\\" + folder.guid + "\\" + path
        return path, virtual_name

    # --------------------------------------------------------------------------------------------->>>
    # this function recives the owner name of certain user and return in list the names of all the folder that the owner owns
    # the function is returning the virtual name given by the client and not the real guid name
    def get_folders_names_by_owner(self, params):
        # getting the necessary variables from the params dict for the function to work properly
        owner = params["USER_NAME"]

        # puts the Folder,s that belongs to the owner in dict {folder.name,folder.guid}
        dict_of_folders = {}
        for folder in self.folders:
            if folder.owner == owner:
                dict_of_folders[folder.name] = str(folder.guid)

        # to send the dict to the client it has to be astring
        dict_of_folders = dict_to_string(dict_of_folders)

        return build_response("GET_FOLDERS", {"FOLDERS_DICT": dict_of_folders})

    # --------------------------------------------------------------------------------------------->>>
    # this function begins a process of sending to the client a folder saved on the server
    # the function recives the parameters of the client request and returns a compressed folder data
    # the compressed folder will be saved on the sever temporarely and then when the function finishes the compressed file will be earased from the server
    def download_folder(self, params):
        # getting the necessary variables from the params dict for the function to work properly
        path, owner = get_multiple_params(params, ["PATH", "USER_NAME"])

        # arrange the path and the virtual name
        path, virtual_name = self._get_original_path_and_virtual_name(path, owner)

        # if the file exists
        if os.path.isdir(path):
            if not os.path.isdir(".\\temp zip files server"):
                os.makedirs(".\\temp zip files server")

            guid = str(uuid4())  # avoid collision by usibg guid
            zip_folder(path, ".\\temp zip files server\\" + guid + '.zip')
            with open(".\\temp zip files server\\" + guid + '.zip', "rb") as f:
                folder_data = f.read().encode("hex")  # reading the compressed folder

            rmtree(".\\temp zip files server")
            return build_response("DOWNLOAD_FOLDER", {"FOLDER_DATA": folder_data})  # succeded

        return build_response("DOWNLOAD_FOLDER", status="FAILED_PATH_DOES_NOT_EXISTS")


# --------------------------------------------------------------------------------------------->>>
if __name__ == "__main__":
    pass
