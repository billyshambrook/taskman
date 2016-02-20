import posixpath
import threading
import time

import taskman.queue


class Worker(object):
    """ """

    queue_collection = 'queues'

    def __init__(self, name, client, queue_name):
        """ """
        self._name = name
        self._client = client
        self._queue_name = queue_name
        self._queue_path = posixpath.join(self.queue_collection, self._queue_name)
        self._queue = None
        self._session_id = None
        self._kill = threading.Event()

    def start(self):
        """ """
        self._session_id = self._client.session.create(name=self._name, ttl='10s')
        self._queue = taskman.queue.Queue(client=self._client, base_path=self._queue_path, session_id=self._session_id)
        self._start_keep_session_alive()

    def stop(self):
        """ """
        self._kill_keep_session_alive()

    def subscribe(self):
        """ """
        for task in self._queue.subscribe():
            yield task
            time.sleep(2)
            task.cancel()

    def _start_keep_session_alive(self):
        t = threading.Thread(target=self._keep_session_alive)
        t.daemon = True
        t.start()

    def _kill_keep_session_alive(self):
        self._kill.set()

    def _keep_session_alive(self):
        while not self._kill.isSet():
            resp = self._client.session.renew(self._session_id)
            if not isinstance(resp, dict):
                raise RuntimeError
            print('keep-alive sent: {}'.format(self._name))
            time.sleep(5)
