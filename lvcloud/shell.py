import logging

import requests
import sys

from lvcloud.load_balancer import LoadBalancer


def set_key(node, key, value, sync=False):
    return requests.post(node, params={key: [value, sync]})


def get_key_value(node, key):
    return requests.get(node, params={'key': key})


def main():

    self_addr = sys.argv[1]
    other_addrs = sys.argv[2:]
    lb = LoadBalancer(self_addr, other_addrs)

    while True:
        try:
            cmd = input(">> ").split()

            if not cmd:
                continue
            elif cmd[0] == 'set':
                result = lb.set(cmd[1], cmd[2])
            elif cmd[0] == 'get':
                result = lb.get(cmd[1])
            else:
                print('Wrong command!')
                continue

            print(result)

        except Exception as e:
            logging.error("Encountered an error: %s", e)
            # running in background
            while True:
                # just wait for commands to _g_kvstorage
                continue


if __name__ == '__main__':
    main()
