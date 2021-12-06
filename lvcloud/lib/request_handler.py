import urllib.parse

from http.server import BaseHTTPRequestHandler

from pysyncobj import SyncObj
from pysyncobj.batteries import ReplLockManager

# Library to be used anywhere
class RequestHandler(BaseHTTPRequestHandler):
    raft_node = None
    lock_manager = None
    lock_sync_obj = None

    def __init__(self, self_addr, others_addr, raft_class):
        # TODO: Remove hard coded gateway addr
        self.raft_node = raft_class("http://localhost:8000", self_addr, others_addr)
        self.lock_manager = ReplLockManager(autoUnlockTime=75)
        self.lock_sync_obj = SyncObj(self_addr, others_addr, consumers=[self.lock_manager])

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
        status_code = self.raft_node.do_POST(args, self.raft_node, self.lock_manager)
        self.send_headers(status_code)
