"""
Think of AWS SDK. You as a user have configured the API keys. The key would contain a user-id and token/private_key.
This is then sent to an AWS gateway in an encrypted form along with your request.

The gateway then routes your request to the appropriate cluster load balancer magically. This could have multiple hops.
This cluster would first authenticate you by calling some identity server. If authenticated, the cluster would
serve your request. The response would then be served back to you.

We implement a simpler version as follows:
- We do not have any authentication.
- We use paths to emulate user/table/key along with operation type and params.
- A user enters all required params as input.
- An emulator manages network emulation by dropping/delaying/duplicating requests.

This is achieved by doing the following:
lvcloud is our own mini cloud infrastructure. When you make a request using lvcloud SDK, it automatically
routes the request to LVGateway located at localhost:8000. We assume that our gateway is always up, otherwise the
request cannot be made.

It then sends the request to the LVLoadBalancer leader, which registers itself by updating the entry on the gateway
upon election. The load balancer then figures out which host contains the given data and routes the request to that
host. It is the load balancer in lvcloud that decides the partitioning algorithm and maintains them.

Whenever a new machine is launched, the load balancer registers it and adds it to the pool of available machines.
Whenever a machine goes down, the machine is replaced by one of the machines in the pool.

We currently use a basic partitioning scheme. Partition by first character. i.e. keys starting a* go to one machine set
and b* go to a different set of machines. If the number of keys become more than 5, we detect that to be a hot
partition and update the partitions. This would need us to implement moving data and we might skip that.

"""
import logging
from http.server import HTTPServer

from lvcloud.gateway_request_handler import GatewayRequestHandler


class Gateway:
    httpd = None

    def __init__(self, leader_addr, others_addr, port=8000, server_class=HTTPServer, handler_class=GatewayRequestHandler):
        server_address = ('', port)
        handler = handler_class(leader_addr, others_addr)
        self.httpd = server_class(server_address, handler)

    def run(self):
        logging.info('Starting httpd...\n')
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        self.httpd.server_close()
        logging.info('Stopping httpd...\n')

