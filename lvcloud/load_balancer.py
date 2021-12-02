import requests
from pysyncobj import replicated, SyncObjConf, SyncObj
from pysyncobj.node import TCPNode


def update_leader(node, self_address, partner_addresses, sync=False):
    return requests.post(node, params={"type": "update_leader", "self_address": self_address,
                                       "partner_addresses": partner_addresses})


class LoadBalancer(SyncObj):
    def __init__(self, self_address, partner_addresses):
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(LoadBalancer, self).__init__(self_address, partner_addresses, cfg)
        self.__data = {}

    @replicated
    def set(self, key, value):
        self.__data[key] = value

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    # if @replicated -> then we guarantee strong consistentency?
    def get(self, key):
        return self.__data.get(key, None)

    def __onBecomeLeader(self):
        super(LoadBalancer, self).__onBecomeLeader()
        update_leader("localhost:8000", self.selfNode.__address, [node.__address for node in self.otherNodes])
