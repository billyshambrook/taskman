"""Queue module."""
import posixpath


class Queue(object):
    """A distributed queue."""

    _COUNTER_FILL = 10
    TASK_PREFIX = 'task_'

    def __init__(self, client, base_path):
        """
        Initialise the class.

        Args:
            client (:class:`consulate.Consul`): A :class:`consulate.Consul` instance.
            base_path (str): the base path to use in Consul.
        """
        self._client = client
        self._base_path = base_path
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
        """Get a task from the queue."""
        tasks = self._get_avaliable_tasks()
        if not tasks:
            return None
        name, data = tasks[0]
        self._client.kv.delete(name)
        return data

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

    def _get_avaliable_tasks(self):
        """Get all tasks present in the queue."""
        base_task = posixpath.join(self._queue_path, self.TASK_PREFIX)
        tasks = self._client.kv.find(prefix=base_task)
        return sorted(tasks.items())

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
