__author__ = 'daniel'

import os, zipfile, ast


# --------------------------------------------------------------------------------------------->>>
# returns the value of the key following the protocol
def decode_message(message, key_word):
    keys_dict = dict((key, value) for key, value in (item.split('=') for item in message.split('|')))
    return keys_dict.get(key_word)


# --------------------------------------------------------------------------------------------->>>
# recives a protocol message and make s a params dict out of it
def get_params_dict(message):
    keys_dict = dict((key, value) for key, value in (item.split('=') for item in message.split('|')))
    del keys_dict["MSG"]
    return keys_dict


# --------------------------------------------------------------------------------------------->>>
# recives a dict of params and a list of params to return and return a list of those params
def get_multiple_params(params_dict, params_to_get):
    list_to_return = []
    for param in params_to_get:
        list_to_return.append(params_dict[param])
    return list_to_return


# --------------------------------------------------------------------------------------------->>>

# building the response that will be returned to the client
# returns the response that will be send to the client
def build_response(msg, dictionary={}, status="SUCCESS"):
    msg_to_respond = "MSG=" + msg + "_RESPONSE|"  # MSG_RESPONSE
    for key in dictionary:
        msg_to_respond += key + "=" + dictionary[key] + "|"  # arranging any spacial key and value after the protocol
    msg_to_respond += "STATUS=" + status  # if not mentioned otherwise status is SUCCESS
    return msg_to_respond  # returns the response that will be send to the client


# --------------------------------------------------------------------------------------------->>>
# building the response that will be returned to the client
# returns the response that will be send to the client
def build_request(msg, dictionary={}):
    msg_to_request = "MSG=" + msg  # MSG
    for key in dictionary:
        msg_to_request += "|" + key + "=" + dictionary[key]  # arranging any spacial key and value after the protocol
    return msg_to_request  # returns the response that will be send to the client


# --------------------------------------------------------------------------------------------->>>
# turns a list to s string
def list_to_string(list1):
    return str(list1)


# --------------------------------------------------------------------------------------------->>>
# turns a string to alist
def string_to_list(string):
    string = string.replace("[", "").replace("]", "").replace("'", "")
    list1 = string.split(",")
    return [x.strip() for x in list1]


# --------------------------------------------------------------------------------------------->>>
# this function unzips a folder
def unzip_folder(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)


# --------------------------------------------------------------------------------------------->>>
# turns a dict to a string
def dict_to_string(dict1):
    return str(dict1)


# --------------------------------------------------------------------------------------------->>>
# turns a string into a dict
def string_to_dict(dict1):
    return ast.literal_eval(dict1)


# --------------------------------------------------------------------------------------------->>>
# turns a boolean to string
def bool_to_str(bool1):
    return str(bool1)


# --------------------------------------------------------------------------------------------->>>
# turns a string to boolean
def str_to_bool(bool1):
    return ast.literal_eval(bool1)


# --------------------------------------------------------------------------------------------->>>
# this function changes the path acoording to the parameters
# index indicates the loction of the name to be removed from the path
# if insert_new_name is not None instead of the file being popped will be inserted  insert_new_name
# the new path will always be returned if return_popped_path is True then also the popped name will be returned
def change_path(path, index, insert_new_name=None, return_popped_path=False):
    path = path.split("\\")
    popped_path = path.pop(index)
    if insert_new_name:
        path.insert(index, insert_new_name)
    if return_popped_path:
        return "\\".join(path), popped_path
    return "\\".join(path)


# --------------------------------------------------------------------------------------------->>>
# removes the tow first bits of a path. a bit is a sub string that is found between tow back slashes
def dir_rmv_first_two(path):
    path = path.split("\\")
    path.pop(0)
    path.pop(0)
    return "\\".join(path)


# --------------------------------------------------------------------------------------------->>>
# this functions checks if the path ends with "\\" if it does the func returns the path without those
def check_path_end(path):
    if path.endswith("\\"):
        path = path[:-1]
    return path


# --------------------------------------------------------------------------------------------->>>
# Check whether 'str' contains ANY of the chars in 'set'
def contains_any(str, set):
    return 1 in [char in str for char in set]


# --------------------------------------------------------------------------------------------->>>
# deletes a file according to the path recived
def delete_local_file_path(path):
    if os.path.isfile(path):
        os.remove(path)


# --------------------------------------------------------------------------------------------->>>
# this function zips an entire folder
def zip_folder(foldername, filename, includeEmptyDIr=True):
    empty_dirs = []
    zip = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(foldername):
        empty_dirs.extend([dir for dir in dirs if os.listdir(os.path.join(root, dir)) == []])
        for name in files:
            zip.write(os.path.join(root, name))
        if includeEmptyDIr:
            for dir in empty_dirs:
                zif = zipfile.ZipInfo(os.path.join(root, dir) + "/")
                zip.writestr(zif, "")
        empty_dirs = []
    zip.close()
