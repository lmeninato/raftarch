import logging
from http.server import HTTPServer

from lvcloud.request_handler import RequestHandler


class Server:
    httpd = None

    def __init__(self, self_addr, others_addr, port, raft_class, server_class=HTTPServer):
        server_address = ('', port)
        handler = RequestHandler(self_addr, others_addr, raft_class)
        self.httpd = server_class(server_address, handler)

    def run(self):
        logging.info('Starting httpd...')
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        self.httpd.server_close()
        logging.info('Stopping httpd...')
