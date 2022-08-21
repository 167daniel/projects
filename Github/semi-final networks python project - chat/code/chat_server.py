__author__ = 'public'


import SocketServer
import socket
import errno
import Queue


class Message():
    def __init__(self, sender_user_name, content, time):
        self.sender_user_name = sender_user_name  #sender of message
        self.content = content  #content of message
        self.time = time  #the time when the message was sent


class User():
    def __init__(self, user_name, password, status, user_address):
        self.user_name = user_name
        self.password = password
        self.status = status
        self.user_address = user_address
        self.inbox = Queue.Queue()


class List_of_users():
    def __init__(self):
        self.list_of_users = [] #a list of Users
        self.list_of_users.extend([User("shaked", "025662393", True, ""), User("daniel", "025662393", False, "")])  #2 Users just for debugging

    #handling a sign up request. the new user the details are inserted to a User and the usr is added to the list_of_users
    #returns the response that will be send to the client
    def sign_up_message(self, user_name, password, user_address):
        #checking if the new User user_name already exists, if it the function will return a FAILED_ALREADY_EXISTS status message.
        for user in self.list_of_users:
            if user.user_name == user_name: #checking if the new User user_name already exists
                    return build_response("SIGN_UP", status="FAILED_ALREADY_EXISTS")  #returns the response that will be send to the client

        #in case that a user will disconnect without logging out
        global current_connected_user_name
        current_connected_user_name = user_name

        self.list_of_users.append(User(user_name, password, True, user_address))  #append the new User to the List_of_users
        return build_response("SIGN_UP")  #returns the response that will be send to the client

    #handling a sign in request. checks if the user details are recognized or not, if not the function will return a FAILED_PASSWORD_INCORRECT status message or a USER_NAME_UNRECOGNIZED status message
    #returns the response that will be send to the client
    def sign_in_message(self, user_name, password, user_address):
        for user in self.list_of_users:  #scanning all the users
            if user.user_name == user_name and not user.status: #if the user was found
                if not password == user.password: #if the password isnt right
                    return build_response("SIGN_IN", status="FAILED_PASSWORD_INCORRECT") # password is wrong

                #password and user_name are matching the user details
                # in case that a user will disconnect without logging out
                global current_connected_user_name
                current_connected_user_name = user.user_name
                #sign in user and save his current address
                user.status = True
                user.user_address = user_address
                return build_response("SIGN_IN") #succesfully signed in

        return build_response("SIGN_IN", status="USER_NAME_UNRECOGNIZED")  #returns the response that will be send to the client

    #handling a log out request.
    #returns the response that will be send to the client
    def log_out_message(self, user_name):
        for user in self.list_of_users:  #scanning all the users
            if user.user_name == user_name:
                user.status = False #logging out User
                break
        return build_response("LOG_OUT") #returns the response that will be send to the client. User logged out

    #puting the chat message in the receiver inbox
    def put_message_in_receiver_inbox(self, sender_user_name, receiver_user_name, content, time):
        user=self.user_by_name(receiver_user_name) # getting the User
        user.inbox.put(Message(sender_user_name, content, time)) # creating a message from the details that were received from the client and putting the message in the receiver User inbox

    #getting the User by the User user_name
    #returns the User
    def user_by_name(self, name):
        for user in self.list_of_users:
            if user.user_name==name:
                return user

    #cheking if there is any new message awaiting in the inbox for the client
    #if there is no messages returns "NO_MESSAGES" else returns the oldest message in inbox
    def check_inbox(self, user_name):  #if inbox not empty the function will return the Queue of the messages (the inbox) else the function will return "NO_MESSAGES"
        for user in self.list_of_users:
            if user.user_name == user_name:
                if user.inbox.qsize() == 0:  #Returns the size of the queue. Note that because of the multi-threaded environment, the size can change at any time, making this only an approximation of the actual size.
                    return "NO_MESSAGES"  #there is no messages in the inbox
                global inbox_not_empty_flag
                if user.inbox.qsize() == 1: #there is one message in the inbox so no need to check again for other messages
                    inbox_not_empty_flag = False
                else:                           # since there are more awaiting messages the client has to ask to receive them
                    inbox_not_empty_flag = True
                return user.inbox.get()  #returns he oldest message in inbox


#returns the value of the key following the protocol
def decode_message(message, key_word):
    keys_dict = dict((key, value) for key, value in (item.split('=') for item in message.split('|')))
    return keys_dict.get(key_word)


#putting the message into the receiver inbox
#returns the response that will be send to the client
def send_message(sender_user_name, receiver_user_name, content, time):
        User_List.put_message_in_receiver_inbox(sender_user_name, receiver_user_name, content, time) #put message in receiver box
        return build_response("SEND_MESSAGE")  #returns the response that will be send to the client


#receives every message the client sent and Aiming the message details to the function that is built for handling this kind of message
#returns the response that will be send to the client
def handle_message(message, user_address):
    message_type = decode_message(message, "MSG") #getting the message type by protocol
    user_name = decode_message(message, "USER_NAME")  #getting the User user_name

    #handling a GET_VERSION message
    if message_type == "GET_VERSION":
        return build_response("GET_VERSION", {"VERSION": "1"}) #returns the response that will be send to the client (the response obtains the version)

    #handling a SIGN_UP and a SIGN_IN type messages since they both need the user password
    elif message_type == "SIGN_UP" or message_type == "SIGN_IN":
        password = decode_message(message, "PASSWORD")

        #handling a SIGN_UP message type
        if message_type == "SIGN_UP":
            return User_List.sign_up_message(user_name, password, user_address) #signing up the User and returns the response that will be send to the client

       #handling a SIGN_IN message type
        elif message_type == "SIGN_IN":
            return User_List.sign_in_message(user_name, password, user_address) #signing in the User and returns the response that will be send to the client

    #handling a LOG_OUT message type
    elif message_type == "LOG_OUT":
            return User_List.log_out_message(user_name) #logging out the user and returns the response that will be send to the client

    #handling a VIEW_CONNECTED_LIST message type
    elif message_type == "VIEW_CONNECTED_LIST":
            return connected_users_list(user_name) #returns the response that will be send to the client (the response obtains the list of connected users)

    #handling a SEND_MESSAGE message type
    elif message_type == "SEND_MESSAGE":

        #preapearing the details received from the client message to the send_message function
        sender_user_name = decode_message(message, "SENDER_USER_NAME")
        receiver_user_name = decode_message(message, "RECEIVER_USER_NAME")
        content = decode_message(message, "CONTENT")
        time = decode_message(message, "TIME")

        return send_message(sender_user_name, receiver_user_name, content, time) #putting message in receiver inbox and returns the response that will be send to the client

    #handling a RECEIVE_MESSAGE message type
    elif message_type == "RECEIVE_MESSAGE":
        #checking if there is any new message awaiting in the inbox if there is a message that was in the inbox will be returned else "NO_MESSAGE" will be returned
        incoming_message = User_List.check_inbox(user_name)
        if incoming_message == "NO_MESSAGES":  #inbox is empty
            return build_response("RECEIVE_MESSAGE", {"INBOX_STATUS": "NO_MESSAGES"}) #returns the response that will be send to the client

        else:  #inbox has still a message in it but since we used get() maybe its empty now so we will use the flag to check it
            #preparation of details for sending message to client
            sender_user_name = incoming_message.sender_user_name
            content = incoming_message.content
            time = incoming_message.time

            #returning the response that will be sended to the client
            global inbox_not_empty_flag
            if inbox_not_empty_flag:  #if there is more than one messages awaiting in the inbox
                return build_response("RECEIVE_MESSAGE",{"INBOX_STATUS": "MORE_AWAITING_MESSAGES", "SENDER_USER_NAME": #the client will have to check again for more messages
                sender_user_name,"CONTENT": content, "TIME": time})

            #else there is no more awaiting messages in inbox
            return build_response("RECEIVE_MESSAGE", {"INBOX_STATUS": "NO_MORE_MESSAGES", "SENDER_USER_NAME": #inbox empty and no need to check for more messages for a while
                sender_user_name, "CONTENT": content, "TIME": time})


# building the response that will be returned to the client
#returns the response that will be send to the client
def build_response(msg, dictionary={}, status="SUCCESS"):
    msg_to_respond = "MSG=" + msg + "_RESPONSE|"  #MSG_RESPONSE
    for key in dictionary:
        msg_to_respond += key+"=" + dictionary[key]+"|"  # arranging any spacial key and value after the protocol
    msg_to_respond += "STATUS=" + status #if not mentioned otherwise status is SUCCESS
    return msg_to_respond  #returns the response that will be send to the client


#returns a list of the connected Users not including the user that will receive this list
def connected_users_list(user_name):
    connected_users = [] #the list of the connected users
    for user in range(len(User_List.list_of_users)): # scanning all the users in List_of_users
        if User_List.list_of_users[user].user_name != user_name and User_List.list_of_users[user].status: #User connected and he isnt the one who will receive this list
            connected_users.append(User_List.list_of_users[user].user_name) #append th User to the list connected users
    return build_response("VIEW_CONNECTED_LIST",
                          {"CONNECTED_USERS_LIST": str(connected_users).replace("[", "").replace("]", "")})  ##returns a list of the connected Users not including the user that will receive this list


class RequestHandler(SocketServer.BaseRequestHandler):

    # setupping the connection
    def setup(self):
        print self.client_address, 'connected!'

    #handling all the communication with the client except the setup step
    def handle(self):
        try:
            #GET_VERSION request
            message = self.request.recv(1024)
            self.request.send(handle_message(message, self.client_address)) #sending a response

            #SIGN_UP or SIGN_IN request
            message = self.request.recv(1024)

            # SIGN_UP request. the loop will continue until that the client will send a user_name that doesnt already exists
            while decode_message(message, "MSG") == "SIGN_UP":
                self.request.send(handle_message(message, self.client_address))  #sending a response
                message = self.request.recv(1024)

            # SIGN_IN request. SIGN_UP request. the loop will continue until that the client will send the right details of the User user_name and password
            while decode_message(message, "MSG") == "SIGN_IN":
                self.request.send(handle_message(message, self.client_address))  #sending a response
                message = self.request.recv(1024)

            #this loop will continue to work until the client decides to disconnect from the server
            # the loop is handling the following messages types: VIEW_CONNECTED_LIST, SEND_MESSAGE, LOG_OUT and RECEIVE_MESSAGE
            while 1:
                self.request.send(handle_message(message, self.client_address))  #sending a response
                message = self.request.recv(1024)

        # if client disconnected
        except socket.error, e:
            if e.errno == errno.ECONNRESET:
                return

    def finish(self):
        print self.client_address, 'disconnected!'
        handle_message("MSG=LOG_OUT|USER_NAME=" + current_connected_user_name, self.client_address) #logging out the User since he disconnected without logging out

#attention! remember that threads are using the same memory! the code is taking advantage of this fact.
inbox_not_empty_flag = False  #when flag is on it symbolize that there is at least 1 message awaiting for the User in his inbox.

#in case that the user disconnected without logging out the server will log him out automatically and for that the
#server needs the User user_name even after the user disconnects from the server that's why there is a need for this argument
current_connected_user_name = ""

User_List = List_of_users() #the list of users contains a list of the registered users

#server host is a tuple ('host', port)
#starting the socketserver
server = SocketServer.ThreadingTCPServer(('', 5000), RequestHandler)
server.serve_forever()