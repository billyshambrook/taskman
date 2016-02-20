from collections import namedtuple
import json
import sys

import consulate


Task = namedtuple('Task', 'id priority body queue')


class Client(object):
    """ """
    TASK_TEMPLATE = '{queue}/task_{priority}_{id}'
    INITIAL_COUNTER = '00000000001'

    queue_backend_cls = backend.LockingQueue

    def __init__(self, host, port, queue):
        """ """
        self.client = consulate.Consul(host=host, port=port)
        self.queue = queue
        self._counter_key = '{}/counter'.format(self.queue)
        self._ensure_counter()

    def put(self, body, priority=1000):
        """ """
        task_id = self._get_counter()
        task_key = self.get_task_name(priority, task_id)
        self.client.kv[task_key] = json.dumps(body)
        return Task(id=task_id, priority=priority, body=body, queue=self.queue)

    def get_task_name(self, priority, task_id):
        """ """
        return '{}/task_{}_{}'.format(self.queue, priority, task_id)

    def _ensure_counter(self):
        """ """
        if not self.client.kv.get(self._counter_key):
            self.client.kv[self._counter] = self.INITIAL_COUNTER

    def _get_counter(self):
        """ """
        counter = int(self.client.kv[self._counter_key])
        counter += 1
        n = str(counter).zfill(len(self.INITIAL_COUNTER))
        self.client.kv[self._counter_key] = n
        return n
