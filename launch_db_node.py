import sys
import logging

from lvcloud.db.database import Database
from lvcloud.lib.server import Server

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

def main():
    gateway_addr = sys.argv[1]
    self_addr = sys.argv[2]
    other_addrs = sys.argv[3:]

    # start server at 100+port
    port = int(self_addr.split(":")[1]) + 100

    server = Server(self_addr, other_addrs, port, Database, gateway_addr=gateway_addr)
    server.run()


if __name__ == '__main__':
    main()
