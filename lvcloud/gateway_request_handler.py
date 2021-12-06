import logging
import urllib.parse

from http.server import BaseHTTPRequestHandler


# Also contains most of the state for gateway since that'll get update by requests etc.
import requests

from lvcloud.load_balancer import LoadBalancer


def set_key(node, args):
    return requests.post(node, params=args)


def get_key_value(node, args):
    return requests.get(node, params=args)


class GatewayRequestHandler(BaseHTTPRequestHandler):
    lb_leader = None

    def __init__(self, leader_addr):
        self.lb_leader = leader_addr

    def __call__(self, *args, **kwargs):
        """ Handle a request """
        super().__init__(*args, **kwargs)

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        # if "type" in args.keys():
        #     logging.info("Setting leader lb to: %s", args.get("self_address"))
        #     self.lb_leader = args.get("self_address")
        #     self.send_headers(201)
        #     return

        resp = get_key_value(self.lb_leader, args)

        self.send_headers(resp.status_code)
        self.wfile.write(resp.content)

    def send_headers(self, value: int) -> None:
        self.send_response(value)
        self.send_header("Content-type", "text/plain")
        self.end_headers()


    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        if "type" in args.keys():
            logging.info("Setting leader lb to: %s", args.get("self_address"))
            self.lb_leader = args.get("self_address")[0]
            self.send_headers(201)
        else:
            try:
                resp = set_key(self.lb_leader, args)

                self.send_headers(resp.status_code)
            except Exception as e:
                logging.error("Encountered error getting data: %s", e)
