import requests
import sys

from lvcloud.load_balancer import LoadBalancer
from lvcloud.server import Server


def set_key(node, key, value, sync=False):
    return requests.post(node, params={key: [value, sync]})


def get_key_value(node, key):
    return requests.get(node, params={'key': key})


def main():
    self_addr = sys.argv[1]
    other_addrs = sys.argv[2:]

    # start server at 100+port
    port = int(self_addr.split(":")[1]) + 100

    server = Server(self_addr, other_addrs, port, LoadBalancer)
    server.run()


if __name__ == '__main__':
    main()
