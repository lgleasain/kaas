#!/usr/bin/env python2.6

# Copyright 2013 Christopher Neugebauer and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' HTTP server for KAAS. Provides the basic HTTP server implementation;
authentication via HMAC for GET requests. 

At the moment the code is inherently singleton at the moment, and it 
doesn't make much sense to do otherwise -- keynote can only display a 
single slide show at once anyway.

Could stand to have the external server interface tidied up into a single 
class.

Exporting a new show will will disable the server for a while, but update
will happen in place.
'''

import remote_handler
import slideshow

import BaseHTTPServer
import hashlib
import hmac
import random
import SocketServer
import socket
import subprocess
import sys
import threading
import remote_json

import wearscript
import argparse
import time


from email import utils
from os import curdir, sep

''' '''


''' Set AUTHENTICATE to False to enable the HTML interface. '''
AUTHENTICATE = False # HTML will not work if authentication is enabled.

class ServerState(object):
    
    def __init__(self):
        self.show = None # No show until one is generated.
        self.server = None # No server yet.
        self.hashes = set()

STATE = ServerState()
KEY = ""





class KeymoteHTTPServer(BaseHTTPServer.HTTPServer):
    pass

class RemoteHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):

        if not self.authenticate():
            self.auth_fail()
            return

        if self.path == '/kontroller.html':
            f = open(curdir + sep + self.path)	
            self.send_response(200)
	    self.send_header('Content-type','text/html')
	    self.end_headers()
	    self.wfile.write(f.read())            
        else:
            try:
                path = self.path.split('/')[1:]
                response, content_type, body = remote_handler.handle(path, STATE.show, WS)

            except Exception as e:
                self.fail(e)
                raise e

            self.send_response(response)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(body)
        

    def fail(self, exception):
        self.send_response(500)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        #print >> self.wfile, self.path

        print >> self.wfile, exception

    def auth_fail(self):
        self.send_response(400)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

        print >> self.wfile, "Request was not authenticated when it should have been."


    def authenticate(self):
        ''' Verifies that a request is authenticated. To do this,
        we provide two headers:
        X-Kaas-Digest: the hmac-sha256 hex digest of the request
        X-Kass-Nonce: a set of random characters to salt the hash.

        A request is authenticated if and only if:
        - The Digest has not been used to authenticate a request on
        this server.
        - The Digest is equivalent to the digest of:
        self.command + '\n' + self.path + '\n' + X-Kaas-Nonce
        (each encoded as ASCII)
        '''
        return True
        nonce = self.headers["X-Kaas-Nonce"]
        request_digest = self.headers["X-Kaas-Digest"]

        #if request_digest in STATE.hashes:
        #    return False

        STATE.hashes.add(request_digest)

        mac = hmac.new(KEY, digestmod = hashlib.sha256)
        mac.update(self.command)
        mac.update("\n")
        mac.update(self.path)
        mac.update("\n")
        mac.update(nonce)

        #return mac.hexdigest() == request_digest 
        return True

def create_server():
    #socket.error: [Errno 48] Address already in use
    port = 8000
    ip = socket.gethostbyname(socket.gethostname())
    while True:
        try:
            STATE.server = KeymoteHTTPServer(('', port), RemoteHTTPRequestHandler)
            break
        except socket.error as e:
            if e.errno == 48:
                # 48 := port in use.
                port += 1
            else:
                raise e
    return (ip, port)


def serve_forever():
    try:
        STATE.server.serve_forever()
    finally:
        print >> sys.stderr, "Obliterating slideshow..."
        STATE.show.obliterate()

def set_show():
    if STATE.show is not None:
        STATE.show.obliterate()

    STATE.show = None # Cannot serve anything for now
    STATE.show = slideshow.generate()

def get_show():
    return STATE.show

def generate_key():
    ''' Generates a random PIN number to authenticate
    requests with. A PIN is a 6-digit number with at least
    3 unique digits. '''

    global KEY

    k = ""
    while len(set(k)) < 3:
        k = str(random.randint(100000, 999999))

    KEY = k
    return k

def prepare_show():
    if STATE.show is not None:
        STATE.show.prepare()

def start_serving():
    #STATE.server = create_server()
    address = create_server()
    server_thread = threading.Thread(target = serve_forever)
    server_thread.daemon = True
    server_thread.start()

    return address

def stop_serving():
    if STATE.server is not None:
        STATE.server.shutdown()




WS=''

def callback(ws, **kw):
    remote_json.WS = ws
    def get_ping(chan, command, timestamp):
        if command == 'SWIPE_LEFT':
            remote_json.handle_glass('previous', STATE.show)
            slide_number = STATE.show.current_slide
            notes = STATE.show.notes(slide_number)
            print notes
            ws.publish('pong', notes, time.time(), ws.group_device)
        if command == 'SWIPE_RIGHT':
            remote_json.handle_glass('next', STATE.show)
            slide_number = STATE.show.current_slide
            notes = STATE.show.notes(slide_number)
            print notes
            ws.publish('pong', notes, time.time(), ws.group_device)

    ws.subscribe('ping', get_ping)
    ws.handler_loop()
    raw_input();





def main():
    print >> sys.stderr, "Generating export from frontmost keynote slideshow..."
    set_show()
    print >> sys.stderr, "Generating build previews..."
    prepare_show()
    generate_key()
    print >> sys.stderr, "Starting server..."
    address = start_serving()
    print >> sys.stderr, "Now serving on: http://%s:%d" % (address)
    print >> sys.stderr, "The PIN number is: %s" % (KEY)

    wearscript.parse(callback, argparse.ArgumentParser())

    try:
        while True:
            raw_input()
    finally:
        stop_serving()

if __name__ == "__main__":
    main()
