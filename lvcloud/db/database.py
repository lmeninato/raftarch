import logging
import os
import time

import requests
from pysyncobj import replicated, SyncObjConf, SyncObj


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
        if existing_lock is None or existing_lock[0] == client_id:
            self.lock(lock_id, (client_id, current_time))
            return True
        # Lock already acquired by someone else
        return False

    def release(self, lock_id, client_id):
        existing_lock = self.__locks.get(lock_id, None)
        if existing_lock is not None and existing_lock[0] == client_id:
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
            if request_type == "set":
                return self.handle_set(args, lb)
            elif request_type == "get":
                return self.handle_get(args, lb)
            elif request_type == "lock":
                return self.handle_lock(args, lb)
            elif request_type == "unlock":
                return self.handle_unlock(args, lb)
            else:
                logging.error(f"Invalid request type: {request_type}")
                return 400, None
        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
            return 400, None

    def do_POST(self, args, lb):
        request_type = args["type"][0]
        try:
            if request_type == "set":
                return self.handle_set(args, lb)
            elif request_type == "get":
                return self.handle_get(args, lb)
            elif request_type == "lock":
                return self.handle_lock(args, lb)
            elif request_type == "unlock":
                return self.handle_unlock(args, lb)
            else:
                logging.error(f"Invalid request type: {request_type}")
                return 400, None

        except Exception as e:
            logging.error("Encountered error getting data: %s", e)
            return 400, None

    def handle_get(self, args, lb):
        key = args['key'][0]
        sync = args['sync'][0]
        logging.info(f'Getting key: {key} with sync {sync}')
        # TODO: Not really using sync
        value = lb.get(key)

        if value is None:
            return 404, None
        else:
            return 200, value.encode('utf-8')

    def handle_set(self, args, lb):
        key = args['key'][0]
        value = args['value'][0]
        sync = args['sync'][0]
        client_id = 0 if args['client_id'][0] is None else args['client_id'][0]

        logging.info(f"Setting key: {key} and value: {value} with sync: {sync} for {client_id}")
        while not lb.acquire(key, client_id, time.time()):
            time.sleep(5)
        lb.set(key, value, sync=True)
        self.release(key, client_id)

        # TODO: Do exception handling and return status code based on that
        return 201, None

    def handle_lock(self, args, lb):
        attempt_time = time.time()

        key = args['key'][0]
        client_id = 0 if args['client_id'][0] is None else args['client_id'][0]

        logging.info(f"Trying to lock key: {key} for {client_id}")
        # TODO: Wait till you get the lock using a queue
        result = lb.acquire(key, client_id, attempt_time)

        if result:
            return 202, None
        else:
            return 409, None

    def handle_unlock(self, args, lb):
        key = args['key'][0]
        client_id = 0 if args['client_id'][0] is None else args['client_id'][0]

        logging.info(f"Trying to unlock key: {key} for {client_id}")
        lb.release(key, client_id)
        return 202, None
