import random
import sys
from time import time
from heirarchical import HeirarchicalKVStore
from config import get_heirarchical_config, set_cluster_addr_mapping_from_config

def get_random_cluster(clusters):
    return random.sample(clusters, 1)[0]

def build_random_keys(clusters, n=1000):
    cluster_names = list(clusters.keys())
    a_idx = ord('a')
    keys = {}
    for _ in range(n):
        cluster = get_random_cluster(cluster_names)
        chars = [cluster, ","]
        for _ in range(3):
            chars.append(chr(a_idx + random.randint(0, 25)))
        chars = "".join(chars)
        keys[chars] = random.randint(1, 1000)
    return keys

def run_test(config):
    clusters = {}
    set_cluster_addr_mapping_from_config(clusters, config)
    kv_pairs = build_random_keys(clusters)
    hkvstore = HeirarchicalKVStore(config)
    run_simulation(kv_pairs, hkvstore)

def run_simulation(kv_pairs, hkvstore):
    requests = 0
    sets = 0
    gets = 0

    keys = list(kv_pairs)
    end = time() + 60
    while time() < end:
        rand_key = random.choice(keys)
        if random.randint(0, 1):
            # set
            hkvstore.set(rand_key, kv_pairs[rand_key])
            sets += 1
        else:
            # get
            hkvstore.get(rand_key)
            gets += 1
        requests += 1
    
    print(f'Made approximately {requests} requests in 60 seconds.')
    print(f'Made {sets} sets and {gets} gets.')
    return requests

def main():
    if len(sys.argv) < 2:
        print('Usage: %s config.yml')
        sys.exit(-1)

    yaml_path = sys.argv[1]
    config = get_heirarchical_config(yaml_path)
    run_test(config)

if __name__ == "__main__":
    main()