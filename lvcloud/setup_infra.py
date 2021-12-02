import logging

from lvcloud.gateway import Gateway
from lvcloud.load_balancer import LoadBalancer

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.DEBUG)

machines = ["localhost:5000", "localhost:5001", "localhost:5002", "localhost:5003", "localhost:5004", "localhost:5005"]

lb1 = LoadBalancer("localhost:5009", ["localhost:5001", "localhost:5002"])
lb2 = LoadBalancer("localhost:5001", ["localhost:5009", "localhost:5002"])
lb3 = LoadBalancer("localhost:5002", ["localhost:5009", "localhost:5001"])

gateway = Gateway(lb1)
gateway.run()
