#!/usr/bin/env python3

import sys
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

from pysyncobj import SyncObj, SyncObjConf, replicated

_g_kvstorage = None

class KVStorage(SyncObj):
    def __init__(self, selfAddress, partnerAddrs):
        cfg = SyncObjConf(dynamicMembershipChange = True)
        super(KVStorage, self).__init__(selfAddress, partnerAddrs, cfg)
        self.__data = {}

    @replicated
    def set(self, key, value):
        self.__data[key] = value

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    # if @replicated -> then we guarantee strong consistentency?
    def get(self, key):
        return self.__data.get(key, None)

class KVRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            global _g_kvstorage
            args = urllib.parse.parse_qs(self.path[2:])
            key = args['key'][0]
            print(f'Getting key: {key}')
            value = _g_kvstorage.get(key)

            if value is None:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(value.encode('utf-8'))
        except:
            pass

    def do_POST(self):
        try:
            args = urllib.parse.parse_qs(self.path[2:])

            for key, value in args.items():
                val = value[0]
                sync = False
                if len(value) == 2:
                    sync = value[1]
                print(f"setting key: {key} and value: {val} with sync: {sync}")
                _g_kvstorage.set(key, val, sync = sync)
            self.send_response(201)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
        except:
            pass

def get_addrs():
    if len(sys.argv) < 2:
            print('Usage: %s httpport selfHost:port partner1Host:port partner2Host:port' % sys.argv[0])
            sys.exit(-1)

    port = sys.argv[1]
    selfAddr = sys.argv[2]
    partners = sys.argv[3:]

    return int(port), selfAddr, partners

def main():
    '''
    To make request:

    import requests

    # get abc key
    requests.get('http://localhost:8000', params = {'key': 'abc'})
    
    # set abc key to 123
    requests.post('http://localhost:8000', params = {'abc': '123'})

    '''
    global _g_kvstorage
    port, selfAddr, partners = get_addrs()
    print(selfAddr, partners)
    _g_kvstorage = KVStorage(selfAddr, partners)

    httpServer = HTTPServer(('localhost', port), KVRequestHandler)
    httpServer.serve_forever()


if __name__ == "__main__":
    main()