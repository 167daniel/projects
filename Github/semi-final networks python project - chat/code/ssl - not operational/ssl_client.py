import socket, ssl, pprint

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Require a certificate from the server. We used a self-signed certificate
# so here ca_certs must be the server certificate itself.
ssl_sock = ssl.wrap_socket(s, do_handshake_on_connect=True, server_side=True, ca_certs='C:\Users\public.daniel\Desktop\server.orig.crt')

ssl_sock.connect(('127.0.0.1', 10023))


ssl_sock.write("""BLA /password HTTP/1.0\r
        pass: liujhikyhj\n\n""")

data = ssl_sock.read()
print data

ssl_sock.write("""BLA / HTTP/1.0\r
        pass: liujhikyhj\n\n""")
data = ssl_sock.read()
print data

    #note that closing the SSLSocket will also close the underlying socket
ssl_sock.close()