import logging

import requests
from pysyncobj import replicated, SyncObjConf, SyncObj


def update_leader(node, self_address):
    req = {"type": "update_leader", "self_address": self_address}
    res = requests.post(node, params=req)
    logging.info("Sent request to update leader")
    return res


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

    # if @replicated -> then we guarantee strong consistentency
    @replicated
    def get(self, key):
        return self.__data.get(key, None)

    # TODO: Make it work
    # def _onBecomeLeader(self):
    #     super(LoadBalancer, self)._onBecomeLeader()
    #     update_leader("http://localhost:8000", "http://" + self.selfNode.host + ":" + str(self.selfNode.port+100))

    def do_GET(self, args, lb):
        key = args['key'][0]
        logging.info(f'Getting key: {key}')

        try:
            value = lb.get(key)

            if value is None:
                return 404, None
            else:
                return 200, value.encode('utf-8')
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def do_POST(self, args, lb):
        try:
            for key, value in args.items():
                val = value[0]
                sync = False
                if len(value) == 2:
                    sync = value[1]
                logging.info(f"setting key: {key} and value: {val} with sync: {sync}")

                lb.set(key, val, sync=True)

            return 201
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
            return 400
