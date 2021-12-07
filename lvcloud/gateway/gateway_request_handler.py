import logging
import urllib.parse
import requests

from http.server import BaseHTTPRequestHandler


class GatewayRequestHandler(BaseHTTPRequestHandler):
    clusters = None

    def __init__(self, clusters, port_offset=100):
        self.clusters = clusters
        self.num_clusters = len(clusters)
        self.port_offset = port_offset

    def __call__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_node_server(self, nodeport):
        node, port = nodeport.split(":")
        return 'http://' + node + ":" + str(int(port)+self.port_offset)

    def get_cluster(self, key):
        return self.clusters[hash(key) % self.num_clusters]

    def do_GET(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        request_type = args["type"][0]

        try:
            if request_type == "transaction":
                self.handle_txn(args)
            else:
                cluster = self.get_cluster(args['key'][0])
                # Forward request to gateway to the db.
                leader = self.get_node_server(cluster[0])

                logging.info(f"Making request to: {leader}")
                resp = requests.get(leader, params=args)
                self.send_headers(resp.status_code)
                self.wfile.write(resp.content)
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def send_headers(self, value: int) -> None:
        self.send_response(value)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def update_cluster_leader(self, leader):
        leader = leader[7:] # strip http://
        node, port = leader.split(":")
        leader = node + ":" + str(int(port)-100)
        logging.info(f"clusters are: {self.clusters}, leader is: {leader}")
        for cluster in self.clusters:
            if leader in cluster:
                index = cluster.index(leader)
                # move leader to leader slot
                cluster[0], cluster[index] = cluster[index], cluster[0]
                return

    def do_POST(self):
        args = urllib.parse.parse_qs(self.path[2:])
        logging.info("Gateway received request with args: %s", args)

        request_type = args["type"][0]

        try:
            if request_type == "update_leader":
                new_leader = args.get("address")[0]
                logging.info(f"Received new leader address: {new_leader}")
                self.update_cluster_leader(new_leader)
                self.send_headers(201)
            elif request_type == "transaction":
                self.handle_txn(args)
            else:
                cluster = self.get_cluster(args['key'][0])
                leader = self.get_node_server(cluster[0])
                # Forward request to gateway to the db.
                logging.info(f"Making request to: {leader}")
                resp = requests.post(leader, params=args)
                self.send_headers(resp.status_code)

        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def handle_txn(self, args):
        commands = args.get("commands")
        logging.info(f"Received a transaction with commands: {commands}")

        client_id = args.get("client_id")[0]

        resp = None
        for command in commands:
            tokens = command.split()
            cmd_type = tokens[0]
            key = tokens[1]
            value = tokens[2] if cmd_type == 'set' else None

            msg = {
                "type": cmd_type,
                "key": key,
                "sync": False,
                "value": value,
                "client_id": client_id
            }

            cluster = self.get_cluster(key)
            leader = self.get_node_server(cluster[0])
            # Forward request to gateway to the db.
            logging.info(f"Making request to: {leader}")
            resp = requests.get(leader, params=msg)
            if resp.status_code >= 400:
                break
        self.send_headers(resp.status_code)
        self.wfile.write(resp.content)
