import sys

from lvcloud.lb.load_balancer import LoadBalancer
from lvcloud.lib.server import Server


def main():
    self_addr = sys.argv[1]
    other_addrs = sys.argv[2:]

    # start server at 100+port
    port = int(self_addr.split(":")[1]) + 100

    server = Server(self_addr, other_addrs, port, LoadBalancer)
    server.run()


if __name__ == '__main__':
    main()
