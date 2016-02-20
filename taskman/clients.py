""" """
from . import base


class Client(_Taskman):
    def __init__(self, vhost):
        super(Client, self).__init__(vhost)

    def add_task(self, body, priority):
        """ """
        logger.debug('Adding task - priority:{}({}), body:{}'.format(priority, PRIORITY[priority], body))
        self._queue.put(body, PRIORITY[priority])
