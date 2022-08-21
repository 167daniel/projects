__author__ = 'public'


import socket
import sys
import time
import easygui
import thread


#returns the time now
def actual_time():
    return str(time.asctime(time.localtime(time.time())))


#returns a converted string to a list
def convert_string_to_list(string):
    string = string.strip("[]")
    return string.split(",")


#returns the value of the key following the protocol
def decode_message(message, key_word):
    keys_dict = dict((key, value) for key, value in (item.split('=') for item in message.split('|')))
    return keys_dict.get(key_word)


#sending to the server a GET_VERSION message and receiving a response from the server
#if the version of the client doesnt match the server version the program will exit
def check_version():
    server.send("MSG=GET_VERSION")
    version = decode_message(server.recv(1024), "VERSION") #receive and get key

    if version != "1": # the client version doesnt match the server version
        server.close()
        sys.exit("Error message: the version of the client is an old version please use a newer version.")


# opening a passwordbox with one filed to fill and returns what the user typed
#if the user pressed cancel or X the program will exit
def enter_password(msg, title):
    reply = easygui.passwordbox(msg, title) #passwordbox

    if reply is None:  #the user pressed cancel or X
        sys.exit("goodbye")

    return reply


#opening an enterbox with one filed to fill and returns what the user typed
#if the user pressed cancel or X the program will exit
def enter_one_parameter(msg, title):
    reply = easygui.enterbox(msg, title)

    if reply is None:  #the user pressed cancel or X
        sys.exit("goodbye")

    return reply


#sending to the server a request to sign up until the user will choose a user name that doesnt exist already
def sign_up_message(user_name, password):
    server.send("MSG=SIGN_UP|USER_NAME=" + user_name + "|PASSWORD=" + password) #sending to the server a request to sign up
    message = server.recv(1024)

    #user name already exist user has to choose another one (will continue until that a username that doesnt exist already will be chosen)
    while decode_message(message, "STATUS") == "FAILED_ALREADY_EXISTS":
        user_name = enter_one_parameter("sorry but username already exists please type another username",
                                        "error user name already exist")  #user types the new user name he chose
        server.send("MSG=SIGN_UP|USER_NAME=" + user_name + "|PASSWORD=" + password) #sending to the server a request to sign up
        message = server.recv(1024)

    easygui.msgbox("signed up successfully enjoy", title="sign up message")


#sending to the server a request to sign in until that the user details will be submitted correctly
def sign_in_message(user_name, password):
    server.send("MSG=SIGN_IN|USER_NAME=" + user_name + "|PASSWORD=" + password)  #sending to the server a request to sign in
    message = server.recv(1024)

    #the user name that was typed isn't recognized (will continue until that the user name will be recognized)
    while decode_message(message, "STATUS") == "USER_NAME_UNRECOGNIZED":
        user_name = enter_one_parameter("please enter username again", "error user name does not exist") #type user name again
        server.send("MSG=SIGN_IN|USER_NAME=" + user_name + "|PASSWORD=" + password)  #sending to the server a request to sign in with the retyped user name
        message = server.recv(1024)

    #the password that was typed isn't recognized (will continue until that the password will be recognized)
    while decode_message(message, "STATUS") == "FAILED_PASSWORD_INCORRECT":
        password = enter_password("please enter your password again", "error password is incorrect")  #type password again
        server.send("MSG=SIGN_IN|USER_NAME=" + user_name + "|PASSWORD=" + password) #sending to the server a request to sign in with the retyped password
        message = server.recv(1024)

    easygui.msgbox("successfully logged in enjoy", title="sign up message")
    return user_name


#sending to the server a request to log out (logging out will be done automatically if the user disconnects from the server even without the logout message)
def log_out_message(user_name):
    server.send("MSG=LOG_OUT|USER_NAME=" + user_name)  #sending to the server a request to log out
    server.recv(1024)
    #exiting
    server.close()
    sys.exit("logged out successfully!\nfeel free to visit again any time. goodbye")


#sending to the server a request to receive the list of the users that are online (semaphore is used since the function is used during a thread)
#returns the user name of the desired user to chat with
def view_connected_list_message_and_choose_chat(user_name):

    #checking if socket in use
    global semaphore
    message = [""]
    count = 0
    #if message == [""] there is no connected users so the program will check every half a second if there is new connected users and until there will be the while loop will continue
    while message == [""]:
        # if not count == 0 its the first time the loop is taking place and there is no need to sleep since the server wont crash because of "messages overflow"
        if not count == 0:
            time.sleep(0.5)
        while semaphore:
            time.sleep(0.2) #socket in use the program has to wait

        semaphore = True #starting to use the socket so semaphore will deny the other thread from Accessing the socket
        server.send("MSG=VIEW_CONNECTED_LIST|USER_NAME=" + user_name) #asking to see connected users list
        message = server.recv(1024)  # receive the list that is know a string
        semaphore = False # stopped using the socket
        message = decode_message(message, "CONNECTED_USERS_LIST") #getting the list of users from the message
        message = convert_string_to_list(message)  #turn it from a string back to a list

    receiver_user_name = easygui.choicebox("please choose a user to chat with", "list of connected users",
                                           choices=message)  # opens a choicebox of which connected user the user desires to chat with

    if receiver_user_name == "Q" or receiver_user_name == "q": #user wants to quite
        log_out_message(user_name)  #exiting

    return receiver_user_name.replace("\'", "").strip()  #returns the user name of the desired user to chat with


#openning a box for receiving the username and passwordfrom the user and returns those in a list
#if the user pressed cancel or X the program will exit
def enter_pass_and_username():

    #preparation for multpasswordbox of password and user name and opening multpasswordbox
    msg = "Enter login information"
    title = "login"
    fieldNames = ["username",  "Password"]
    fieldsValues = []  # we start with blanks for the values
    fieldValues = easygui.multpasswordbox(msg, title, fieldNames)

    while 1:
        # make sure that none of the fields was left blank
        if fieldValues is None:
           sys.exit("goodbye")

        errmsg = ""
        for i in range(len(fieldNames)):  #check if there is a blank field
            if fieldValues[i].strip() == "":
                errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])  #there is a blank field

        if errmsg == "":
            break  # no problems found

        fieldValues = easygui.multpasswordbox(errmsg, title, fieldNames, fieldValues)  #there is a blank field

    return fieldValues #returns user name and pass in list


#Send message to another client connected to the server and receives chat messages from the client as well as CHANGE messages and Q or q messages
#if the user pressed cancel or X the program will exit
def send_message():
    global semaphore
    global receiver_user_name
    receiver_user_name = view_connected_list_message_and_choose_chat(user_name)  #the user to communicate with

    while 1:
        command = enter_one_parameter("message or a command (CHANGE, Q or q)", "command or message")  #if there isn't a special case this will be the content of rhe message
        #the user pressed cancel or X or Q or q and he wants to quite
        if command is None or command == "q" or command == "Q":
            log_out_message(user_name)
            thread.interrupt_main()
            break
        #the user want to change a chat partner
        elif command == "CHANGE":
            receiver_user_name = view_connected_list_message_and_choose_chat(user_name)
        #the message is a normal chat message
        else:
            print "you:%s (%s)" % (command, actual_time())
            while semaphore: #checking if socket in use
                time.sleep(0.2)  #socket in use the program has to wait
            semaphore = True #starting to use the socket so semaphore will deny the other thread from Accessing the socket
            server.send("MSG=SEND_MESSAGE|SENDER_USER_NAME=" + user_name + "|RECEIVER_USER_NAME=" + receiver_user_name +
                      "|CONTENT=" + command + "|TIME=" + actual_time())
            server.recv(1024)
            semaphore = False # stopped using the socket semaphore will allow the other thread from Accessing the socket


#checking if there is any new chat messages awaiting for the user and if there is the the messages will be printed
def receive_message():
    "Receive data from other clients connected to server"
    while 1:
        global semaphore
        while semaphore: #checking if socket in use
            time.sleep(0.2) #socket in use so we have to wait
        semaphore = True #starting to use the socket so semaphore will deny the other thread from Accessing the socket
        server.send("MSG=RECEIVE_MESSAGE|USER_NAME=" + user_name)
        chat_message = server.recv(1024)
        semaphore = False  #stopped using the socket semaphore will allow the other thread from Accessing the socket
        inbox_status = decode_message(chat_message, "INBOX_STATUS")

        # there is more messages awaiting for the user so the client will ask to get them
        if not inbox_status == "NO_MESSAGES":
            sender_user_name = decode_message(chat_message, "SENDER_USER_NAME")
            chat_message_content = decode_message(chat_message, "CONTENT")
            time_sent = decode_message(chat_message, "TIME")
            print sender_user_name + ": " + chat_message_content + ". (" + time_sent + ")"

        #there is no more messages awaiting for the user so program will wait since if not the server will crash because of "messages overflow"
        if not inbox_status == "MORE_AWAITING_MESSAGES":
            time.sleep(3)

#since we dont want the threads to interrupt each other (by receiving each other responses from the server) the threads will check the flag before using the socket if the
#flag is on the program will wait until it'll turn off and if its on the program will turn on the flag so the other thread wont interrupt the socket sending and receiving process
semaphore = False
receiver_user_name = ""  #the name of the user the message wil be sended too
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("127.0.0.1", 5000))
check_version() #checks the version

#signing up or in to the server
options_list = ["sign in", "sign up"]
sign_up_or_in = easygui.buttonbox("hello and welcome to chat on the web!", title="hello and welcome", choices=options_list)
list_user_and_pass = enter_pass_and_username()
user_name = list_user_and_pass[0]
password = list_user_and_pass[1]

#user pressed cancel or X and he wants to quite
if sign_up_or_in is None:
    sys.exit("goodbye")

#sign up
if sign_up_or_in == options_list[1]:
    sign_up_message(user_name, password)

#sign in
else:
    user_name = sign_in_message(user_name, password)
#welcome and instruction message
easygui.msgbox("enjoy your stay at chat on the web\nyou can always log out by pressing Q\n"
               "here's the list of the users that are currently connected.\nif you want to change the partner of your "
               "conversation type CHANGE.\nimportant! also all the chat messages will be printed and typed in the "
               "console\nthe list of the connected users wont appear until there will be other connected users"
               , title="welcome")
# receiving and sending should be asynchronous but since it is complicated for know im using threads
thread.start_new_thread(receive_message, ()) #this thread will receive the new messages from the server
thread.start_new_thread(send_message, ())  #this thread will send the user messages to the server
try:    #so the program wont quit while in thread
    while 1:
        continue
except:
    sys.exit("goodbye") #thread error close