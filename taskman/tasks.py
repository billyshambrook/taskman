"""Tasks."""
import json
import logging


logger = logging.getLogger(__name__)


class Task(object):
    """Represents a task from the queue."""

    def __init__(self, queue, path, data, session_id):
        """
        Initialise the class.

        Args:
            queue (:class:`.queues.LockingQueue`): A instance of :class:`.queues.LockingQueue` that the task belongs to.
            path (str): The full path to the task.
            data (str): The task data.
            session_id (str): The session UUID that this task is locked by.
        """
        self._queue = queue
        self._path = path
        self._data = data
        self._body = json.dumps(self._data['body'])
        self._session_id = session_id

    def consume(self):
        """Consume the task so that the task isn't picked up again."""
        return self._queue.consume(self.path, self.session_id):

    def cancel(self):
        """Cancel the task to make it available to be picked up again."""
        return self._queue.cancel(self.path, self.session_id)

    @property
    def locked(self):
        """True if the task is locked to the session ID."""
        return True if self.queue._client.kv.get_record(self.path).get('Session') == self.session_id else False

    @property
    def path(self):
        """The full path to the task."""
        return self._path

    @property
    def path(self):
        """The full path to the task."""
        return self._session_id

    @property
    def json_str(self):
        """The body as a JSON string."""
        return self._data['body']

    @property
    def body(self):
        """The body as python types."""
        return self._body

    @property
    def info(self):
        """
        Information about the task.

        This includes:
            * created (datetime): The datetime the task was created.
        """
        return self._data['info']

    @classmethod
    def _from_consul(cls, queue, session_id, d):
        """Create a task from the dictionary given by the Consul HTTP API."""
        logger.debug('Creating task from consul dict...')
        return cls(queue=queue, path=d['Key'], data=d['Value'], session_id=session_id)
