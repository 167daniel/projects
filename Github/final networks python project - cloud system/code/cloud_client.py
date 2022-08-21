__author__ = 'daniel'

from uuid import uuid4
from shutil import rmtree
from distutils.dir_util import copy_tree
from Utils import *
import os, zlib, socket, sys, easygui, Queue, time, folder_monitor, thread, wx


# call wx  gui which is better than easygui
def show_message_dlg(msg, title, style):
    dlg = wx.MessageDialog(parent=None, message=msg,
                           caption=title, style=style)
    dlg.ShowModal()


# --------------------------------------------------------------------------------------------->>>
# this function prepares the system to work
# it verifies that the synchronization folder (from which files and folders will be synced to the server) existst
# also it verifies that the download folder (to which files will be downloaded from the server
# if those folder does not exists they will be created
def prepare_system():
    # if ".\\synchronization folder" does not exist its created if it its truncated
    if os.path.exists(".\\synchronization folder"):
        rmtree(".\\synchronization folder")
    try:
        os.makedirs(".\\synchronization folder")
    except WindowsError:
        time.sleep(0.5)
        os.makedirs(".\\synchronization folder")

    # if .\\temp zip files client folder does not exist its created if it its truncated
    if os.path.exists(".\\temp zip files client"):
        rmtree(".\\temp zip files client")
    os.makedirs(".\\temp zip files client")


# --------------------------------------------------------------------------------------------->>>
# sending to the server a GET_VERSION message and receiving a response from the server
# if the version of the client doesnt match the server version the program will exit
def get_version():
    server.send("MSG=GET_VERSION")
    version = decode_message(server.recv(1024), "VERSION")  # receive and get key

    if version != "1":  # the client version doesnt match the server version
        server.close()
        sys.exit("Error message: the version of the client is an old version please use a newer version.")


# --------------------------------------------------------------------------------------------->>>

# openning a gui box for getting the username and password from the user and returns those in a list
# if the user pressed cancel or X the program will exit
def enter_pass_and_username():
    # preparation for multpasswordbox of password and user name and opening multpasswordbox
    msg = "Enter user information"  # main message of the gui box
    title = "login system"  # title of the box
    fieldNames = ["username", "Password"]  # the fields that the user will have to fill by himself using the keyboard

    # field values is a list of the username and password given by the user
    fieldValues = easygui.multpasswordbox(msg, title, fieldNames)  # show the gui to the computer user

    # this loop runs until every field is filled with something
    while 1:
        errmsg = easygui_check_blank_fields(fieldValues, fieldNames)  # checks if there is any blank field left

        # if errmsg is not "" there is blank fileds and the user will have to fill those
        if not errmsg == "":
            fieldValues = easygui.multpasswordbox(errmsg, title, fieldNames, fieldValues)  # there is a blank field

        else:  # all fields are filled
            break

    return fieldValues[0], fieldValues[1]  # returns user name and pass in list


# --------------------------------------------------------------------------------------------->>>
# recives fieldNames which are the names of the filelds that were shown to the user and fieldValues which is the details that the user have given
# if none of the fieldValues is emptythere is no blank fileds and the function returns errmsg = ""
# else there are blank fields and the function returns errmsg = that is filled with message to the user that will appear in the next gui
# for every blank filed errmsg adds to himself '"%s" is a required field.\n\n' %S represents the name of the blank filed
def easygui_check_blank_fields(fieldValues, fieldNames):
    # check if X was pressed
    if fieldValues is None:
        sys.exit("goodbye")

    # make sure that none of the fields was left blank
    errmsg = ""
    for i in range(len(fieldNames)):  # check if there is a blank field
        if fieldValues[i].strip() == "":
            errmsg = errmsg + (
                '"%s" is a required field.\n\n' % fieldNames[i])  # there is a blank field add it to errmsg

    return errmsg


# --------------------------------------------------------------------------------------------->>>
# this function deals with protocol errors messages recived from the server.
# those errors also have to be notified to the computer user graphiclly and this func is dealing with both
def easygui_protocol_err(err_kind, user_name=None):
    title = "error"  # title of the box
    fieldNames = ["username", "Password"]  # the fields that the user will have to fill by himself using the keyboard
    errmsg = errors[err_kind]

    # if the error is about the user_name the user_name is surely not None so errmsg contains "%s" instead of the real
    # user_name and now the real user_name which was chosen by the user will replace "%s"
    if user_name:
        errmsg = errmsg % user_name

    # breaks when no error is found anymore
    while 1:

        # post the gui with the errors found in errmsg
        fieldValues = easygui.multpasswordbox(errmsg, title, fieldNames)

        # check if there are any blank fields if there arent errmsg == "" else errmsg = a list of the errors to post in the next gui
        errmsg = easygui_check_blank_fields(fieldValues, fieldNames)

        if errmsg == "":  # no errors
            break

    return fieldValues  # those are the final values without any errors


# --------------------------------------------------------------------------------------------->>>
# sending to the server a request to sign up until the user will choose a user name that doesnt exist already
def sign_up():
    user_name, password = enter_pass_and_username()  # ask in gui for user_name and password

    # sending to the server a request to sign up and recieves a response
    server.send("MSG=SIGN_UP|USER_NAME=" + user_name + "|PASSWORD=" + password)
    message = server.recv(1024)

    # while user_name already exists user has to choose another one (will continue until that a username that doesnt exist already will be chosen)
    # or illegal chars has benn inserted into password or user_name
    status = decode_message(message, "STATUS")
    while status in ["FAILED_ALREADY_EXISTS", "FAILED_ILLEGAL_CHAR"]:

        if status == "FAILED_ALREADY_EXISTS":
            # the user_name already exists on the server, ask for new ones
            fieldValues = easygui_protocol_err(status, user_name)

        elif status == "FAILED_ILLEGAL_CHAR":
            fieldValues = easygui_protocol_err(status)

        user_name, password = fieldValues[0], fieldValues[1]

        server.send(
            "MSG=SIGN_UP|USER_NAME=" + user_name + "|PASSWORD=" + password)  # sending to the server a request to sign up
        message = server.recv(1024)

    thread.start_new_thread(show_message_dlg, (
        "sign up successful, synchronization will now begin.\ndo not make cahges yet in synchronization folder!",
        "signed up successfully enjoy", wx.OK))


# --------------------------------------------------------------------------------------------->>>

# sending to the server a request to sign in until that the user details will be submitted correctly
def sign_in():
    user_name, password = enter_pass_and_username()  # ask in gui for user_name and passwors

    server.send(
        "MSG=SIGN_IN|USER_NAME=" + user_name + "|PASSWORD=" + password)  # sending to the server a request to sign in
    message = server.recv(1024)

    # while the user name that was typed isn't recognized (will continue until that the user name will be recognized)
    # or the password that was typed isn't recognized (will continue until that the password will be recognized)
    # litteral: while no status == "succes"
    status = decode_message(message, "STATUS")
    while status in ["FAILED_USER_NAME_UNRECOGNIZED", "FAILED_PASSWORD_INCORRECT"]:
        if status == "FAILED_USER_NAME_UNRECOGNIZED":
            fieldValues = easygui_protocol_err(status,
                                               user_name)  # get new values from the user since user_name does not exist
        else:
            fieldValues = easygui_protocol_err(status)  # get new values from the user since password is wrong

        user_name, password = fieldValues[0], fieldValues[1]

        server.send(
            "MSG=SIGN_IN|USER_NAME=" + user_name + "|PASSWORD=" + password)  # sending to the server a request to sign up
        message = server.recv(1024)

        # for the next loop. if still not status == "SUCCESS" the loop will itterate again
        status = decode_message(message, "STATUS")

    thread.start_new_thread(show_message_dlg, (
        "signed in successfully, enjoy. synchronization will now begin.\ndo not make cahges yet in synchronization folder!",
        "sign in successful", wx.OK))


# --------------------------------------------------------------------------------------------->>>
# recives a path of a file to be uploaded to the server and sends it to the server
def sync_to_server_upload_file(path):
    # if file does exist
    if os.path.isfile(path):
        with open(path, "rb") as f:
            data = f.read()

        # adapts to the folder hierarchy on the server
        path = dir_rmv_first_two(path)  # removes ".\synchronization folder\"

        server.send("MSG=UPLOAD|PATH=" + path + "|FILE_DATA=" + str(zlib.compress(data)).encode("hex"))
        server.recv(1024)


# --------------------------------------------------------------------------------------------->>>
# recives a path. the path is a path of the file on the server and not on the current computer
# asks the server to send the file
def download_file(server_path):
    # adapts to the folder hierarchy on the server
    server_path = dir_rmv_first_two(server_path)

    server.send("MSG=DOWNLOAD|PATH=" + server_path)
    message = server.recv(99999999)

    # decode the file
    file_data = decode_message(message, "FILE")
    file_data = zlib.decompress(file_data.decode("hex"))

    # gets just the file name without the hole path
    file_name = server_path.split("\\")[-1]

    # if the file does not exist  its being created. does trancuates
    with open(".\downloads\\" + file_name, "wb+") as f:
        f.write(file_data)


# --------------------------------------------------------------------------------------------->>>
# gets a path of a folder or file and announces to the server that he has to create the same file or folder too
def sync_to_server_create(path):
    # if path exists
    if os.path.exists(path):

        if os.path.isfile(path):
            is_file = True  # the path being syncrd to the server is a file

        # else path is a folder
        else:
            is_file = False  # the path being syncrd to the server is a folder

        # adapts to the folder hierarchy on the server
        path = dir_rmv_first_two(path)

        # the last part is the file/folder that does not exist yet on the server so the path still need adaption
        path, new_name = change_path(path, len(path.split("\\")) - 1, return_popped_path=True)

        # if path is empty the user has created a file in the main sync folder area. its forbbiden!
        # the file will be deleted
        if path == "" and is_file:
            delete_local_file_path(".\\synchronization folder\\" + new_name)

            # the message wont block the sync since its a thread. were not using here easygui since its buggy with threads
            thread.start_new_thread(show_message_dlg, (
                "creating files in the main sync folders area is forbidden.\ntherefore the file was deleted.",
                "ERROR: forbidden", wx.ICON_EXCLAMATION))

            return True  # the server does not need to create the file we just deleted. there is no point in sending him a message plus the deletion of the file will have to be ignored

        server.send(build_request("CREATE", {"PATH": path, "NEW_NAME": new_name, "IS_FILE": bool_to_str(is_file)}))
        server.recv(1024)


# --------------------------------------------------------------------------------------------->>>
# gets a path of a file or folder and the file/folder old_name and current name as new_name
# sends a request to the server to tcreate the same path\folder in the server
def sync_to_server_rename(path, old_name, new_name):
    if os.path.exists(path):

        # adapts to the folder hierarchy on the server
        path = dir_rmv_first_two(path)

        # if path is not a main sync folder. we need becuase if it a main sync path == "" nad if this operation will be
        # executed on path = "" we will get stuck with "\\" at the start of the path
        if not path == "":
            path = path + "\\" + old_name

        # path is a main sync folder but now path is empty so we have to fill it with the real path which is actually old_name
        # avoids getting "//" on the start of the file
        else:
            path = old_name

        server.send(build_request("RENAME", {"PATH": path, "NEW_NAME": new_name}))
        server.recv(1024)


# --------------------------------------------------------------------------------------------->>>
# gets a path of a folder or file and announces to the server that he has to delete the same file or folder too
def sync_to_server_delete(path, ignore=False):
    # true when a file was deleted from the main sync folder area. since putting fle there is forbidden.there is no need
    #  to upate the server about it
    if ignore:
        return

    # adapts to the folder hierarchy on the server
    path = dir_rmv_first_two(path)  # removes ".\synchronization folder\"

    server.send(build_request("DELETE", {"PATH": path}))
    server.recv(1024)


# --------------------------------------------------------------------------------------------->>>
# requests from the server the list of the folder that belongs to the current connected user_name
# returns dict of key: folder name, value: folder name on the server (guid)
def get_main_sync_folders():
    server.send(build_request("GET_FOLDERS"))
    message = server.recv(1024)
    return string_to_dict(decode_message(message, "FOLDERS_DICT"))


# --------------------------------------------------------------------------------------------->>>
# this function syncs and download the main sync folders of the user from the server
def sync_from_server(dict_main_folders):
    # folder= folder name
    for folder in dict_main_folders:

        server.send(build_request("DOWNLOAD_FOLDER", {"PATH": folder}))  # ask for the zipped main_sync_folder

        # the folder.zip may be a large file so we have to make sure all the file has arrived
        # if it does not end with succes the file has not arrived entirely since the STATUS is sent after the FILE_DATA by protocol
        message = ""
        while 1:
            data = server.recv(99999999)
            message += data
            if message.endswith("SUCCESS"): break

        # decode the file and create on the computer as zip file
        file_data = decode_message(message, "FOLDER_DATA")
        file_data = file_data.decode("hex")
        guid = str(uuid4())
        # if the file does not exists its created. trancuates
        with open((".\\temp zip files client\\" + guid + ".zip"), "wb") as f:
            f.write(file_data)

        # unzip the file and change excracted folder guid name to the name given by the user
        try:
            unzip_folder(".\\temp zip files client\\" + guid + ".zip", ".\\temp zip files client")
            os.rename("./temp zip files client/users_folders/" + dict_main_folders.get(folder),
                      "./temp zip files client/users_folders/" + folder)

        # the folder is empty and therefore the zip file has raise a corrupted error
        except zipfile.BadZipfile:

            # if .\temp zip files client\users_folders does not exist create it
            if not os.path.isdir(".\\temp zip files client\\users_folders"):
                os.makedirs(".\\temp zip files client\\users_folders")

            # create the empty folder
            os.makedirs(".\\temp zip files client\\users_folders\\" + folder)


# --------------------------------------------------------------------------------------------->>>
# this function moves the main sync folders that are found in ".\\temp zip files client\\users_folders"
# to their right place (".\\synchronization folder")
# also the function removes temp zip files client folder
def arrange_folders():
    if os.path.isdir(".\\temp zip files client\\users_folders"):
        copy_tree(".\\temp zip files client\\users_folders", ".\\synchronization folder")
    if os.path.isdir(".\\temp zip files client"):
        rmtree(".\\temp zip files client")


# --------------------------------------------------------------------------------------------->>>
# this function monitors ".\\synchronization folder" every change that is made in this path will be reported
# accordingly the function will ask the server to copy the changes being made in the folder
def watch_for_changes():
    files_changed = Queue.Queue()  # a queue of the changes in the monitored folder
    folder_monitor.Watcher(".\\synchronization folder", files_changed)  # call the monitor
    deleted_main_sync_file_ignore = False
    while 1:
        try:
            file_type, path, action = files_changed.get_nowait()  # pop out of the queue the next change

            # the path is given in unicode and now being turned to normal str
            path = str(path)

            # if a folder\file was renamed
            if action == "Renamed to something":
                # the old name is not the correct path anymore so wrer cutting it out of the path
                path, old_name = change_path(path, len(path.split("\\")) - 1, return_popped_path=True)

                # next action is renamed from something and we need now original_path is th dir of the current file
                file_type, original_path, action = files_changed.get_nowait()

                # this path is also given in unicode and now being turned to normal str
                original_path = str(original_path)

                # cut the new_name out of the path
                original_path, new_name = change_path(original_path, len(path.split("\\")), return_popped_path=True)
                sync_to_server_rename(path, old_name, new_name)

            # if a file was updated
            elif (file_type, action) == ("file", "Updated"):
                sync_to_server_upload_file(path)

            # if a file\folder was deleted
            elif file_type == "<deleted>":
                sync_to_server_delete(path, deleted_main_sync_file_ignore)
                deleted_main_sync_file_ignore = False

            # if a folder\file was created
            elif action == "Created":
                # if file deleted is true then the user have created a file in the main sync area which is forbbiden the
                #  file was therefore delted and now the monitor noticed it so we need to remove this action from the queue
                # plus there will be an updated action so we have to remove the actions twice
                deleted_main_sync_file_ignore = sync_to_server_create(path)


        # no new actions
        except Queue.Empty:
            pass
        time.sleep(0.5)


# --------------------------------------------------------------------------------------------->>>
errors = {
    "FAILED_ALREADY_EXISTS": 'the user name "%s" already exists.\n\n',
    "FAILED_USER_NAME_UNRECOGNIZED": 'the user name "%s" does not exists.\n\n',
    "FAILED_PASSWORD_INCORRECT": 'password is incorrect.\n\n',
    "FAILED_ILLEGAL_CHAR": 'ERROR: illegal chars have been entered\nthose are illegal chars: space / | \ @ > < ? * : ! "' + "'\n"

}


# --------------------------------------------------------------------------------------------->>>
# Main program
# --------------------------------------------------------------------------------------------->>>
def main():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(("127.0.0.1", 5000))
    get_version()  # checks if the version of the client and the server are the same

    # ------------------------------------>>>
    # signing up or in to the server
    options_list = ["sign in", "sign up"]
    sign_up_or_in = easygui.buttonbox("hello and welcome to the cloud system", title="welcome",
                                      choices=options_list)  # sign_up_or_in will be filled with one of ["sign in", "sign up"]
    # if X was pressed and the user to quite
    if sign_up_or_in is None:
        sys.exit("goodbye")

    # sign up

    if sign_up_or_in == options_list[1]:
        sign_up()

    # sign in
    else:
        sign_in()
    # ------------------------------------>>>
    prepare_system()  # create temp zip files client folder and synchronization folder
    dict_main_folders = get_main_sync_folders()  # get from the server the folders name and guid name that the user owns {file.name: file.guid}
    sync_from_server(dict_main_folders)  # download the data that belongs to the user from the server
    arrange_folders()  # rearrange the folers after last actions

    # notify the server that synchronization from server is finished
    thread.start_new_thread(show_message_dlg, (
        "synchronization from server is finished.\nyou can now synchronize files and folder to the server.",
        "synchronizatiom message", wx.OK))

    watch_for_changes()  # monitor the sync folder and warn on changes


if __name__ == "__main__":
    app = wx.App(False)
    main()
