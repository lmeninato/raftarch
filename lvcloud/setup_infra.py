import logging
import os
import subprocess

from lvcloud.gateway import Gateway
from lvcloud.load_balancer import LoadBalancer

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)

machines = ["localhost:5003", "localhost:5001", "localhost:5002"]

procs = []

for i in machines:
    process = subprocess.Popen(['python3', 'shell.py', i] + [j for j in machines if j != i],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
    procs.append(process)


gateway = Gateway("localhost:5003", ["localhost:5001", "localhost:5002"])
gateway.run()
