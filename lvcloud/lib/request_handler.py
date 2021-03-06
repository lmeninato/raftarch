import urllib.parse

from http.server import BaseHTTPRequestHandler


# Library to be used anywhere
class RequestHandler(BaseHTTPRequestHandler):
    raft_node = None

    def __init__(self, self_addr, others_addr, raft_class, gateway_addr='http://localhost:8000'):
        # TODO: Remove hard coded gateway addr
        self.raft_node = raft_class(gateway_addr, self_addr, others_addr)

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_headers(self, value: int) -> None:
        self.send_response(value)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        status_code, result = self.raft_node.do_GET(args, self.raft_node)
        self.send_headers(status_code)
        if result is not None:
            self.wfile.write(result)

    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        resp = self.raft_node.do_POST(args, self.raft_node)
        self.send_headers(resp[0])
