import logging
import subprocess

from lvcloud.gateway.gateway import Gateway

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

clusters = generate_local_clusters(2, k=3)

procs = []

for cluster in clusters:
    for node in cluster:
        process = subprocess.Popen(['python3', 'launch_db_node.py', 'http://localhost:8000', node] + [j for j in cluster if j != node],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
        logging.info(f'Starting up node: {node} with process id: {process.pid}')
        procs.append(process)

gateway = Gateway(clusters, port = 8000)
gateway.run()

for process in procs:
    logging.info(f"terminating process: {process}")
    process.terminate()
