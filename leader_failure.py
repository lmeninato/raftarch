import logging
import random
import subprocess

from time import time

from lvcloud.gateway.gateway import Gateway
from client import txn

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

def generate_local_clusters(n, k=3):
    '''
    n: Number of Raft clusters to utilize in database
    k: Number of nodes per raft cluster
    '''
    clusters = []
    port = 5001
    host = 'localhost'

    for _ in range(n):
        cluster = []
        for _ in range(k):
            node = host + ':' + str(port)
            cluster.append(node)
            port += 1
        clusters.append(cluster)
    return clusters

def start_db_nodes(clusters):
    procs = []

    for cluster in clusters:
        for node in cluster:
            process = subprocess.Popen(['python3', 'launch_db_node.py', node] + [j for j in cluster if j != node],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
            logging.info(f'Starting up node: {node} with process id: {process.pid}')
            procs.append(process)
            
    return procs

def build_random_keys(n=1000):
    keys = {}
    for _ in range(n):
        chars = []
        for _ in range(3):
            chars.append(chr(ord('a') + random.randint(0, 25)))
        chars = "".join(chars)
        keys[chars] = random.randint(1, 1000)
    return keys

def run_simulation(kv_pairs, gateway = "http://localhost:8000"):
    requests = 0
    sets = 0
    gets = 0
    errors = 0

    kill_time_printed = False

    requests_over_time = []

    keys = list(kv_pairs)
    start = time()
    end = start + 60
    while time() < end:
        ts = time()
        if not kill_time_printed and (ts > start + 10):
            print(f'10 seconds have passed')
            kill_time_printed = True
        res = 'err'
        rand_key = random.choice(keys)
        if random.randint(0, 1):
            # set
            try:
                txn(gateway, ['txn 0', f'set {rand_key} {kv_pairs[rand_key]}'])
                res = 'set'
            except:
                errors += 1
            sets += 1
        else:
            # get
            try:
                txn(gateway, ['txn 0', f'get {rand_key}'])
                res = 'get'
            except:
                errors += 1
            gets += 1
        requests += 1
        requests_over_time.append((ts, res))
    
    print('requests: {}, sets: {}, gets: {}, errors: {}'.format(requests, sets, gets, errors))
    return requests_over_time

def results_to_csv(reqs):
    with open('results_leader_failure.csv', 'w+') as f:
        f.write("time,command\n")
        for req in reqs:
            ts, cmd = req
            f.write(f"{ts},{cmd}\n")

if __name__ == "__main__":
    kv_pairs = build_random_keys()
    requests_over_time = run_simulation(kv_pairs)
    results_to_csv(requests_over_time)