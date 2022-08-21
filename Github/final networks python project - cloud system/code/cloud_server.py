__author__ = 'daniel'

from User_system import User_system
from Folder_manager import Folder_manager
from Utils import *
import socket, errno, SocketServer


# --------------------------------------------------------------------------------------------->>>
class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True


class RequestHandler(SocketServer.BaseRequestHandler):
    # setupping the connection
    def setup(self):
        print self.client_address, 'connected!'

    # --------------------------------------------------------------------------------------------->>>

    # handling all the communication with the client except the setup step
    def handle(self):

        # in case that the user disconnected without logging out the server will log him out automatically and for that the
        # server needs the User user_name even after the user disconnects from the server that's why there is a need for this argument
        global current_connected_user_name

        # this loop will continue to work until the client decides to disconnect from the server
        # the loop is handling evrey message type
        while 1:
            try:
                message = self.request.recv(9999999)

                # if client disconnected in a proper way
                if not message:
                    print self.client_address, 'disconnected!'

                    # notice that anyway USER_NAME and USER_ADDRESS will be changed in the handle_message function so for now
                    # its not important whats written in them.
                    handle_message(
                        "MSG=LOG_OUT|USER_NAME=user_name|USER_ADDRESS=user_address",
                        self.client_address,
                        current_connected_user_name)  # logging out the User since he disconnected without logging out
                    return

                if decode_message(message, "MSG") in ["SIGN_UP", "SIGN_IN"]:
                    current_connected_user_name = decode_message(message, "USER_NAME")

                self.request.send(
                    handle_message(message, self.client_address, current_connected_user_name))  # sending a response

            # if client disconnected by raising exception
            except socket.error, e:
                if e.errno == errno.ECONNRESET:
                    print self.client_address, 'disconnected!'

                    # notice that anyway USER_NAME and USER_ADDRESS will be changed in the handle_message function so for now
                    # its not important whats written in them.
                    handle_message(
                        "MSG=LOG_OUT|USER_NAME=use_name|USER_ADDRESS=user_address",
                        self.client_address,
                        current_connected_user_name)  # logging out the User since he disconnected without logging out
                    return


# --------------------------------------------------------------------------------------------->>>

def get_version(params):
    return build_response("GET_VERSION", {
        "VERSION": "1"})  # returns the response that will be send to the client (the response obtains the version)


# --------------------------------------------------------------------------------------------->>>
# handels every message from the client and routes to the right function that will take care of the message
def handle_message(message, user_address, user_name=None):
    cmd = decode_message(message, "MSG")  # cmd = "MSG' content

    if cmd not in commands:  # if unknown command
        return build_response("ERROR", status="FAILED_COMMAND_NOT_FOUND")

    # fill USER_ADDRESS and USER_NAME keys with values
    params = get_params_dict(message)
    params["USER_ADDRESS"] = user_address
    params["USER_NAME"] = user_name

    # if the client is not connected yet to his an account hes allowed to sent just messages from "GET_VERSION" or "SIGN_UP" or "SIGN_IN" type
    if user_name is None and decode_message(message, "MSG") not in ["GET_VERSION", "SIGN_UP", "SIGN_IN"]:
        return build_response("ERROR", status="FAILED_NO_ACCESS_PERMISSION")

    return commands[cmd](params)


# --------------------------------------------------------------------------------------------->>>

server_user_system = User_system()
server_folder_manager = Folder_manager()

# dict of commands that can be recived from the clients
commands = {
    "GET_VERSION": get_version,
    "SIGN_UP": server_user_system.sign_up,
    "SIGN_IN": server_user_system.sign_in,
    "LOG_OUT": server_user_system.log_out,
    "DELETE": server_folder_manager.delete_folder_or_file,
    "DOWNLOAD": server_folder_manager.download_file,
    "RENAME": server_folder_manager.rename_folder_or_file,
    "UPLOAD": server_folder_manager.upload_file,
    "CREATE": server_folder_manager.create_folder_or_file,
    "GET_FOLDERS": server_folder_manager.get_folders_names_by_owner,
    "DOWNLOAD_FOLDER": server_folder_manager.download_folder
}

# in case that the user disconnected without logging out the server will log him out automatically and for that the
# server needs the User user_name even after the user disconnects from the server that's why there is a need for this argument
current_connected_user_name = None


# --------------------------------------------------------------------------------------------->>>
# Main program
# --------------------------------------------------------------------------------------------->>>
def main():
    # server host is a tuple ('host', port)
    # starting the socketserver
    server = SocketServer.ThreadingTCPServer(('127.0.0.1', 5000), RequestHandler)
    server.serve_forever()


# --------------------------------------------------------------------------------------------->>>
if __name__ == "__main__":
    main()
