import logging
import subprocess
import sys

from lvcloud.gateway.gateway import Gateway

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S', level=logging.INFO)

if len(sys.argv) == 2 and sys.argv[1] == '2':
    clusters = [['10.10.1.1:5001', '10.10.1.2:5001', '10.10.1.3:5001'], ['10.10.1.1:5002', '10.10.1.2:5002', '10.10.1.3:5002']]
else:
    clusters = [['10.10.1.1:5001', '10.10.1.2:5001', '10.10.1.3:5001']]

gateway = Gateway(clusters, port = 8000)
gateway.run()
