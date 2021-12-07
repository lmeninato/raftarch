import logging

import requests

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)


def post(node, key, value, sync=False):
    msg = {
        "type": "set",
        "key": key,
        "value": value,
        "sync": sync
    }
    return requests.post(node, params=msg)


def get(node, key, sync=False):
    msg = {
        "type": "get",
        "key": key,
        "sync": sync
    }
    return requests.get(node, params=msg)


def lock(node, lock_type, key, sync=True):
    msg = {
        "type": lock_type,
        "key": key,
        "sync": sync
    }
    return requests.post(node, params=msg)


def main():
    while True:
        try:
            cmd = input(">> ").split()

            if not cmd:
                continue
            elif cmd[0] == 'set':
                result = post("http://localhost:8000", cmd[1], cmd[2])
            elif cmd[0] == 'get':
                result = get("http://localhost:8000", cmd[1])
            elif cmd[0] == 'lock' or cmd[0] == 'unlock':
                result = lock("http://localhost:8000", cmd[0], cmd[1])
            else:
                print('Usage: set <key> <value>')
                print('\t get <key>')
                continue

            if result.status_code == 200:
                print(result.text)
            elif result.status_code == 201 or result.status_code == 202:
                print("Done!")
            elif result.status_code == 404:
                print(f"Key: {cmd[1]} not found!")
            elif result.status_code == 409:
                print(f"Unable to lock {cmd[1]}!")
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
