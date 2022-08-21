__author__ = 'public'

import BaseHTTPServer, SimpleHTTPServer
import ssl
import socket


class SecureHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_BLA(self):
        '''handle in GET request'''
        print "BLA"
        print self.path
        print self.headers
        self.wfile.write("dddd")
        print "send"
        print self.client_address, self.address_string(), self.date_time_string(), self.server_version
        return

def run_ser():
    while True:
        httpd.handle_request()

httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 10023), SecureHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, certfile='C:\Users\public.daniel\Desktop\server.crt', keyfile='C:\Users\public.daniel\Desktop\server.key', do_handshake_on_connect=True, server_side=True)
run_ser()

