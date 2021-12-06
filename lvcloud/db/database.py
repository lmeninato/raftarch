import logging

import requests
from pysyncobj import replicated, SyncObjConf, SyncObj
from pysyncobj.batteries import ReplLockManager


def get_fail_callback(self, data):
    logging.error("callback for get. the failure was %s", data)


class Database(SyncObj):
    gateway_addr = None

    def __init__(self, gateway_addr, self_address, partner_addresses):
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(Database, self).__init__(self_address, partner_addresses, cfg)
        self.gateway_addr = gateway_addr
        self.__data = {}

    @replicated
    def set(self, key, value, sync=True):
        self.__data[key] = value

    @replicated
    def pop(self, key):
        self.__data.pop(key, None)

    @replicated
    def get(self, key, callback=get_fail_callback, timeout=20, sync=True):
        return self.__data.get(key, None)

    # TODO: Updating leader takes too much time and causes too many re-elections. Make it async?
    def _onBecomeLeader(self):
        super(Database, self)._onBecomeLeader()
        self.update_leader()

    def update_leader(self):
        logging.info("Sending request to update DB leader info at Gateway")

        address = "http://" + self.selfNode.host + ":" + str(self.selfNode.port + 100)
        msg = {
            "type": "update_leader",
            "address": address
        }
        return requests.post(self.gateway_addr, params=msg)

    def do_GET(self, args, lb):
        request_type = args["type"][0]

        try:
            if request_type == "get":
                key = args['key'][0]
                sync = args['sync'][0]
                logging.info(f'Getting key: {key} with sync {sync}')
                # TODO: Not really using sync
                value = lb.get(key)

                if value is None:
                    return 404, None
                else:
                    return 200, value.encode('utf-8')
            else:
                logging.error(f"Invalid request type: {request_type}")
                return 400, None
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)

    def do_POST(self, args, lb, lock_manager: ReplLockManager):
        request_type = args["type"][0]
        try:
            if request_type == "set":
                key = args['key'][0]
                value = args['value'][0]
                sync = args['sync'][0]

                logging.info(f"Setting key: {key} and value: {value} with sync: {sync}")
                lb.set(key, value, sync=True)

                # TODO: Do exception handling and return status code based on that
                return 201
            elif request_type == "lock":
                key = args['key'][0]

                # TODO: Wait till you get the lock using a queue
                logging.info(f"Trying to lock key: {key}")
                result = lock_manager.tryAcquire(key, sync=True, timeout=10)
                if result:
                    return 202
                else:
                    return 409
            elif request_type == "unlock":
                key = args['key'][0]

                logging.info(f"Trying to unlock key: {key}")
                result = lock_manager.release(key, sync=True)
                if result:
                    return 202
                else:
                    return 409
            else:
                logging.error(f"Invalid request type: {request_type}")
                return 400

        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
            return 400
