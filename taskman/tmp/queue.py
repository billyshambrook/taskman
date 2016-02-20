"""Queue module."""
import json
from operator import itemgetter
import posixpath
import time


class Task(object):
    """ """

    def __init__(self, queue, path, data):
        """ """
        self._queue = queue
        self._path = path
        self._data = data

    def cancel(self):
        """ """
        self._queue.cancel(self._path)

    def consume(self):
        """ """
        self._queue.consume(self._path)

    def lock(self):
        """ """
        self._queue.lock(self._path)

    @property
    def data(self):
        """ """
        return self._data

    @property
    def json(self):
        """ """
        return json.dumps(self._data)

    @property
    def path(self):
        """ """
        return self._path

    @property
    def locked(self):
        """ """
        return True if self._queue.owned(self._path) else False

    @property
    def name(self):
        """ """
        return posixpath.basename(self._path)


class Queue(object):
    """A distributed queue."""

    _COUNTER_FILL = 10
    TASK_PREFIX = 'task_'

    def __init__(self, client, base_path, session_id):
        """
        Initialise the class.

        Args:
            client (:class:`consulate.Consul`): A :class:`consulate.Consul` instance.
            base_path (str): the base path to use in Consul.
            session_id (str): the session id to lock tasks with.
        """
        self._client = client
        self._base_path = base_path
        self._session_id = session_id
        self._queue_path = posixpath.join(self._base_path, 'queue', '')
        self._counter_path = posixpath.join(self._queue_path, 'counter')
        self._ensure_counter()
        self._ensure_queue()

    def _ensure_counter(self):
        """Ensure counter exists in Consul."""
        if self._counter_path not in self._client.kv:
            self._client.kv[self._counter_path] = ''.zfill(self._COUNTER_FILL)

    def _ensure_queue(self):
        """Ensure queue exists in Consul."""
        if self._queue_path not in self._client.kv:
            self._client.kv[self._queue_path] = None

    def get(self):
        """Get the first task from the queue that can be locked."""
        tasks = self._get_avaliable_tasks() or []
        for task in tasks:
            print('checking if its locked')
            if self.lock(task['Key']):
                return Task(queue=self, data=task['Value'], path=task['Key'])

    def cancel(self, task_path):
        """
        Cancel a task.

        This will release the lock on the task.
        """
        self._client.kv.release_lock(item=task_path, session=self._session_id)

    def consume(self, task_path):
        """Delete task from queue."""
        if self.lock(task_path):
            print('deleting')
            self._client.kv.delete(item=task_path)
        else:
            print('Not locked to this worker')

    def put(self, value, priority=100):
        """
        Put a task into the queue.

        Args:
            value (str): Task data.
            priority (int): An optional priority as an integer with at most 3 digits.
                Lower values signify higher priority.
        """
        task_name = '{}{:03d}_{}'.format(self.TASK_PREFIX, priority, self._counter)
        path = posixpath.join(self._queue_path, task_name)
        self._client.kv[path] = value

    def lock(self, task_path):
        """ """
        return self._client.kv.acquire_lock(task_path, session=self._session_id)

    def locked(self, task_path):
        """ """
        raw_task = c.kv.get_record('queue/task_000005')
        return True if raw_task and raw_task.get('Session') else False

    def owned(self, task_path):
        """ """
        raw_task = c.kv.get_record('queue/task_000005')
        return True if raw_task and raw_task.get('Session') == self._session_id else False

    def subscribe(self):
        """ """
        while True:
            print('looking for a task')
            task = self.get()
            if task:
                yield task
            print('no task found, sleeping')
            time.sleep(2)

    def _get_avaliable_tasks(self):
        """
        Get all available tasks present in the queue.

        Any tasks that have been locked will not be returned. A locked task is determined if
        it has a session binded to it.
        """
        return (t for t in self._get_all_tasks() if not t.get('Session'))

    def _get_all_tasks(self):
        """Get all tasks present in the queue."""
        base_task = posixpath.join(self._queue_path, self.TASK_PREFIX)
        available_tasks = self._client.kv._get_list(params=[base_task], query_params={'recurse': None})
        print(len(available_tasks))
        return (task for task in available_tasks)

    @property
    def _counter(self):
        """Current task counter."""
        count = int(self._client.kv[self._counter_path])
        count += 1
        count_str = str(count).zfill(self._COUNTER_FILL)
        self._client.kv[self._counter_path] = count_str
        return count_str

    def __len__(self):
        """Queue length."""
        return len(self._get_avaliable_tasks())
