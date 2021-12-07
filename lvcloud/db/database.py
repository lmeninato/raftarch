import logging
import os
import time

import requests
from pysyncobj import replicated, SyncObjConf, SyncObj
from pysyncobj.batteries import ReplLockManager


def get_fail_callback(self, data):
    logging.error("callback for get. the failure was %s", data)


class Database(SyncObj):
    gateway_addr = None

    def __init__(self, gateway_addr, self_address, partner_addresses, auto_unlock_time=30):
        cfg = SyncObjConf(dynamicMembershipChange=True)
        super(Database, self).__init__(self_address, partner_addresses, cfg)
        logging.info(f"My pid in db is {os.getpid()}")
        self.gateway_addr = gateway_addr
        self.__data = {}
        self.__locks = {}
        self.__auto_unlock_time = auto_unlock_time

    @replicated
    def set(self, key, value):
        self.__data[key] = value

    @replicated
    def lock(self, key, value):
        self.__locks[key] = value

    @replicated
    def pop(self, key, sync=True):
        self.__data.pop(key, None)

    # @replicated
    def get(self, key):
        return self.__data.get(key, None)

    def acquire(self, lock_id, client_id, current_time):
        existing_lock = self.__locks.get(lock_id, None)
        logging.info(f"trying to lock {lock_id} and got the value {existing_lock}")
        # Auto-unlock old lock
        if existing_lock is not None:
            if current_time - existing_lock[1] > self.__auto_unlock_time:
                logging.info(f"setting lock as None since diff is {current_time - existing_lock[1]} vs "
                             f"the unlock time {self.__auto_unlock_time}")
                existing_lock = None
        # Acquire lock if possible
        if existing_lock is None:
            self.lock(lock_id, (client_id, current_time))
            return True
        # Lock already acquired by someone else
        return False

    def release(self, lock_id, client_id):
        existing_lock = self.__locks.get(lock_id, None)
        if existing_lock is not None:
            self.lock(lock_id, None)

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

    def do_POST(self, args, lb):
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
                attempt_time = time.time()

                key = args['key'][0]
                logging.info(f"Trying to lock key: {key}")
                # TODO: Wait till you get the lock using a queue
                result = self.acquire(key, 0, attempt_time)

                if result:
                    return 202
                else:
                    return 409
            elif request_type == "unlock":
                key = args['key'][0]

                logging.info(f"Trying to unlock key: {key}")
                self.release(key, 0)
                return 202
            else:
                logging.error(f"Invalid request type: {request_type}")
                return 400

        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
            return 400
