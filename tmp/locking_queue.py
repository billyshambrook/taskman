import posixpath


class LockingQueue(object):
    """ """
    INITIAL_COUNT = '0000000001'

    def __init__(self, client, path, task_prefix='task_'):
        """ """
        self._client = client
        self._path = path
        self._counter_path = posixpath.join(path, 'counter')
        self._task_prefix = task_prefix
        self._ensure_paths()

    def _ensure_paths(self):
        """ """
        for p in [self._path, self._counter_path]:
            if not p in self._client.kv:
                self._client.kv[p] = self.INITIAL_COUNT

    def _get_tasks(self):
        """ """
        keys = self._client.kv.find(prefix=posixpath.join(self._path, self._task_prefix), separator='/')
        for k in keys:
            yield k

    def __len__(self):
        """ """
        return len(list(self._get_tasks))
