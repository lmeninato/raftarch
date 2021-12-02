import requests


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

            print(result)


        except EOFError:
            # running in background
            while True:
                # just wait for commands to _g_kvstorage
                continue


if __name__ == '__main__':
    main()
