import sys
import requests
from config import get_heirarchical_config, set_cluster_addr_mapping_from_config

def set_key(node, key, value, sync=False):
    return requests.post(node, params = {key: [value, sync]})

def get_key_value(node, key):
    return requests.get(node, params = {'key': key})

class HeirarchicalKVStore():
    def __init__(self, config):
        self.config = config
        self.cluster_addrs = {}
        set_cluster_addr_mapping_from_config(self.cluster_addrs, config)

    def get_cluster_and_key(self, key):
        # assume key has format "[a|b],key"
        split_key = key.split(",")
        if len(split_key) != 2:
            print("Usage: set [cluster],key value e.g. set a,abc 123")
            return None, None
        cluster, key = key.split(",")
        if cluster not in self.cluster_addrs:
            print(f"Cluster: {cluster} not found in {self.clusters}")
            return None, None
        
        return self.cluster_addrs[cluster], key

    def set(self, key, value, sync=False):
        cluster_addr, key = self.get_cluster_and_key(key)
        if cluster_addr and key:
            resp = set_key(cluster_addr, key, value, sync)
            if resp.status_code == 201:
                print(f"Sent request to set {key} => {value} (sync={sync})")
            else:
                print(f"Error setting {key} => {value} (sync={sync})")

    def get(self, key):
        cluster_addr, key = self.get_cluster_and_key(key)
        if cluster_addr and key:
            resp = get_key_value(cluster_addr, key)
            if resp.status_code == 200:
                print(resp.text)
            elif resp.status_code == 404:
                print(f"Key: {key} not found!")
            else:
                print(f"Error looking up key: {key}")
        return None

def main():
    if len(sys.argv) < 2:
        print('Usage: %s config.yml')
        sys.exit(-1)

    yaml_path = sys.argv[1]
    config = get_heirarchical_config(yaml_path)

    hkvstore = HeirarchicalKVStore(config)

    while True:
        try:
            cmd = input(">> ").split()
        except EOFError:
            # running in background
            while True:
                # just wait for commands to _g_kvstorage
                continue
        if not cmd:
            continue
        elif cmd[0] == 'set':
            hkvstore.set(cmd[1], cmd[2])
        elif cmd[0] == 'get':
            hkvstore.get(cmd[1])
        else:
            print('Wrong command')

if __name__ == '__main__':
    main()