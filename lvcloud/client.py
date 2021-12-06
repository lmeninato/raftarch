import logging

import requests

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)

def set_key(node, key, value, sync=False):
    return requests.post(node, params={key: [value, sync]})


def get_key_value(node, key):
    return requests.get(node, params={'key': key})


def main():
    while True:
        try:
            cmd = input(">> ").split()

            if not cmd:
                continue
            elif cmd[0] == 'set':
                result = set_key("http://localhost:8000", cmd[1], cmd[2])
            elif cmd[0] == 'get':
                result = get_key_value("http://localhost:8000", cmd[1])
            else:
                print('Wrong command!')
                continue

            if result.status_code == 200:
                print(result.text)
            elif result.status_code == 201:
                print("Done!")
            elif result.status_code == 404:
                print(f"Key: {cmd[1]} not found!")
            else:
                print(f"Error looking up key: {cmd[1]}")

        except Exception as e:
            logging.error("Encountered an error: %s", e)
            # running in background
            while True:
                # just wait for commands to _g_kvstorage
                continue


if __name__ == '__main__':
    main()
