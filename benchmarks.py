import logging
import multiprocessing
import random
import subprocess
import sys

import concurrent.futures
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


def generate_random_requests(kv_pairs, n=10000):
    keys = kv_pairs.keys()
    request_list = []
    for i in range(n):
        rand_key = random.choice(keys)
        if random.randint(0, 1):
            request_list.append(['txn 0', f'set {rand_key} {kv_pairs[rand_key]}'])
        else:
            request_list.append(['txn 0', f'get {rand_key}'])
    return request_list


def send_request(req):
    txn(gateway, req)
    return


def results_to_csv(reqs, thread_id=None):
    if thread_id is None:
        file_out = 'benchmarks.csv'
    else:
        file_out = f'benchmarks_threaded_{thread_id}.csv'
    with open(file_out, 'w+') as f:
        f.write("time,command\n")
        for req in reqs:
            ts, cmd = req
            f.write(f"{ts},{cmd}\n")


if __name__ == "__main__":
    gateway = "http://localhost:8000"
    kv_pairs = build_random_keys()
    requests = generate_random_requests(kv_pairs, 10000)
    print('warming up db..')

    for k, v in kv_pairs:
        txn(gateway, ['txn 0', f'set {k} {v}'])

    print('db warmed up.')

    cpus = multiprocessing.cpu_count()
    print('using {} cpus', cpus)

    if len(sys.argv) > 1:
        # multithreading is OK since work is IO-bound, not CPU-bound

        exec_time = 0
        with multiprocessing.Manager() as manager:
            start = time()
            print('start time is {}', start)
            pool = multiprocessing.Pool(processes=cpus)

            for req in requests:
                pool.apply_async(send_request, args=(req, ))

            pool.close()
            pool.join()

            end = time()
            print('end time is {}', end)

            exec_time = end-start
            print('exec time is {}', exec_time)

    else:
        requests_over_time = run_simulation(kv_pairs)
        results_to_csv(requests_over_time)
