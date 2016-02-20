import json
import time

from .consul import Consul


class Worker(object):
    """ """

    def __init__(self, host, port, queue_path):
        """ """
        self.client = Consul(host=host, port=port)
        self.queue_name = queue_name

    def subscribe(self):
        """ """
        while True:
            task_keys = self.client.kv.find(prefix='{}/task_'.format(self.queue_name), separator='/')
            if task_keys:
                if not isinstance(task_keys, list):
                    task_keys = [task_keys]

                for k in sorted(task_keys):
                    try:
                        task = self.client.kv[k]
                        with self.client.lock.acquire(k):
                            print(k)
                            yield task
                            self.client.kv.delete(k)
                        break
                    except:
                        pass
            else:
                time.sleep(1)
