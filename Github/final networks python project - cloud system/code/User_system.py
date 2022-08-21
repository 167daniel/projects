__author__ = 'daniel'

from Utils import *
from hashlib import sha1


# for every user an object of User kind is created
class User():
    def __init__(self, user_name, password, logged_in, user_address=None):
        self.user_name = user_name
        self.password = password
        self.logged_in = logged_in
        self.user_address = []
        if user_address:  # user adress is only given when list_of_folder is already loaded
            self.user_address.append(user_address)

    def __str__(self):
        return self.user_name + ",IsLogin:" + str(self.logged_in)


# --------------------------------------------------------------------------------------------->>>
# --------------------------------------------------------------------------------------------->>>
# this class takes care of everything that is related to logging in and out and alsotakes care of registration
class User_system():
    def __init__(self):
        self.list_of_users = []  # a list of Users
        self.list_of_users_path = "list_of_users"  # path of the file list of users which has to be located in the same path of the
        # cloud_server.py file

        # the user system is being called for the first time so there is a need to reload all the users that are registerd from the list of users file
        # into the virtual list of users
        with open(self.list_of_users_path, 'a+') as content_file:
            content_file.seek(0)
            self._load_users(content_file.read())

    # --------------------------------------------------------------------------------------------->>>
    # handling a sign up request. the new user the details are inserted to a User and the usr is added to the list_of_users
    # returns the response that will be send to the client
    def sign_up(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        user_name, password, user_address = get_multiple_params(params, ["USER_NAME", "PASSWORD", "USER_ADDRESS"])

        # checks tha all the chars in the user_name and password are legal
        illegal_chars = [" ", "/", "|", "\\", "@", ">", "<", "?", "*", ":", "!", '"', "'"]
        if contains_any(user_name, illegal_chars) or contains_any(password, illegal_chars):
            return build_response("SIGN_UP",
                                  status="FAILED_ILLEGAL_CHAR")  # returns the error response that will be send to the client

        # checking if the new User user_name already exists, if it the function will return a FAILED_ALREADY_EXISTS status message.
        for user in self.list_of_users:
            if user.user_name == user_name:  # checking if the new User user_name already exists
                return build_response("SIGN_UP",
                                      status="FAILED_ALREADY_EXISTS")  # returns the response that will be send to the client

        password = sha1(password).hexdigest()  # calculate a hash for the password
        user = User(user_name, password, True, None)
        self.list_of_users.append(user)  # append the new User to the List_of_users
        user.user_address.append(user_address)

        with open(self.list_of_users_path, 'a') as list_file_content:  # append the new user to the list of users file
            list_file_content.write(user_name + " " + password + "\n")

        return build_response("SIGN_UP")  # returns the response that will be send to the client

    # --------------------------------------------------------------------------------------------->>>
    # handling a sign in request. checks if the user details are recognized or not, if not the function will return a FAILED_PASSWORD_INCORRECT status message or a FAILED_USER_NAME_UNRECOGNIZED status message
    # returns the response that will be send to the client
    def sign_in(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        user_name, password, user_address = get_multiple_params(params, ["USER_NAME", "PASSWORD", "USER_ADDRESS"])

        for user in self.list_of_users:  # scanning all the users
            if user.user_name == user_name:  # if the user was found
                # if user_address in user.user_address:
                #     return build_response("SIGN_IN", status="FAILED_USER_ALREADY_LOGGED_IN")

                if not sha1(password).hexdigest() == user.password:  # if the password isnt right
                    return build_response("SIGN_IN", status="FAILED_PASSWORD_INCORRECT")  # password is wrong

                # sign in user and save his current address
                user.logged_in = True
                if user_address:
                    user.user_address.append(user_address)
                return build_response("SIGN_IN")  # succesfully signed in

                # handling a log out request.
                # returns the response that will be send to the client

                # the user was not found

        return build_response("SIGN_IN", status="FAILED_USER_NAME_UNRECOGNIZED")

    # --------------------------------------------------------------------------------------------->>>
    # logging the user out of the server
    def log_out(self, params):

        # getting the necessary variables from the params dict for the function to work properly
        user_name, user_address = get_multiple_params(params, ["USER_NAME", "USER_ADDRESS"])

        for user in self.list_of_users:  # scanning all the users
            if user.user_name == user_name:
                user.user_address.remove(
                    user_address)  # the current user adress of the user is being disconnected (the user may still be connected from other computers)
                if not user.user_address:  # if the user is completley disconnected from server and thers no more computers that are logged in
                    user.logged_in = False  # logging out User
                break
        return build_response("LOG_OUT")  # returns the response that will be send to the client. User logged out

    # --------------------------------------------------------------------------------------------->>>
    # loading the users from list of users file to virtual list_of_users
    def _load_users(self, file_content):
        for line in file_content.splitlines():
            user_name, password = line.split(" ")
            self.list_of_users.append(User(user_name, password, False))

    # --------------------------------------------------------------------------------------------->>>
    # returning all the users that are connected to the system
    def _get_connected_users(self):
        connected_users = []
        for user in self.list_of_users:
            if user.logged_in:
                connected_users.append(user.user_name)
        return connected_users

    # --------------------------------------------------------------------------------------------->>>
    # returning the user list
    def __str__(self):
        str_to_return = "Users List:\n"
        for user in self.list_of_users:
            str_to_return += str(user) + "\n"
        return str_to_return
