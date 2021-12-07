import logging
import subprocess

from lvcloud.gateway.gateway import Gateway

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.DEBUG)

machines = ["localhost:5003", "localhost:5001", "localhost:5002"]

procs = []

# for i in machines:
#     process = subprocess.Popen(['python3', 'launch_lb.py', i] + [j for j in machines if j != i],
#                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
#     procs.append(process)


gateway = Gateway("http://localhost:5101", 8000)
gateway.run()

for process in procs:
    process.terminate()
