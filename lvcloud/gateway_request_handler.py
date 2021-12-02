import logging
import urllib.parse

from http.server import BaseHTTPRequestHandler


# Also contains most of the state for gateway since that'll get update by requests etc.
from lvcloud.load_balancer import LoadBalancer


class GatewayRequestHandler(BaseHTTPRequestHandler):
    lb = None

    def __init__(self, lb_leader):
        self.lb = lb_leader
        # super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """ Handle a request """
        super().__init__(*args, **kwargs)

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        key = args['key'][0]
        logging.info(f'Getting key: {key}')

        try:
            value = self.lb.get(key)

            if value is None:
                self.send_headers(404)
            else:
                self.send_headers(200)
                self.wfile.write(value.encode('utf-8'))
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def send_headers(self, value: int) -> None:
        self.send_response(value)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        if "type" in args.keys():
            logging.info("Setting leader lb to: %s", args.get("self_address"))
            self.lb = LoadBalancer(args.get("self_address"), args.get("partner_addresses"))
        else:
            try:

                for key, value in args.items():
                    val = value[0]
                    sync = False
                    if len(value) == 2:
                        sync = value[1]
                    logging.info(f"setting key: {key} and value: {val} with sync: {sync}")

                    self.lb.set(key, val, sync=True)

                self.send_headers(201)
            except Exception as e:
                logging.error("Encountered error getting data: %s", e)
