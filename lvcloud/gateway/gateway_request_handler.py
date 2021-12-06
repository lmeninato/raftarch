import logging
import urllib.parse
import requests

from http.server import BaseHTTPRequestHandler


class GatewayRequestHandler(BaseHTTPRequestHandler):
    lb_leader = None

    def __init__(self, leader_addr):
        self.lb_leader = leader_addr

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        request_type = args["type"][0]

        try:
            # Forward request to gateway to the db.
            resp = requests.get(self.lb_leader, params=args)
            self.send_headers(resp.status_code)
            self.wfile.write(resp.content)
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def send_headers(self, value: int) -> None:
        self.send_response(value)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        request_type = args["type"][0]

        try:
            if request_type == "update_leader":
                self.lb_leader = args.get("address")[0]
                logging.info("Setting leader db to: %s", self.lb_leader)
                self.send_headers(201)
            else:
                # Forward request to gateway to the db.
                resp = requests.post(self.lb_leader, params=args)
                self.send_headers(resp.status_code)

        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
