import socket, ssl

bindsocket = socket.socket()
bindsocket.bind(('0.0.0.0', 10023))
bindsocket.listen(5)

def do_something(connstream, data):
    print "do_something:", data
    return False

def deal_with_client(connstream):
    data = connstream.read()
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket, do_handshake_on_connect=False,
                                 server_side=False,
                                 certfile="C:\Users\public.daniel\Desktop\server.crt",
                                 keyfile="C:\Users\public.daniel\Desktop\server.key")
    try:
        deal_with_client(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()