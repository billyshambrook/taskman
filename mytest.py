from collections import namedtuple
import logging
import posixpath
import random
import threading
import time
import uuid

import consulate


logger = logging.getLogger('taskman')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


PRIORITY = {'low': 100, 'mid': 75, 'high': 50, 'urgent': 20}




class Worker(Taskman):
    def __init__(self, vhost):
        super(Worker, self).__init__(vhost)
        self._worker_session_id = None
        self._task_session_id = None

        self._kill_flag = threading.Event()
        self._start()
        self._queue.register_worker(self._worker_session_id)

    def _start(self):
        """ """
        self._worker_session_id = self._client.session.create(behavior='delete', ttl='10s')
        self._task_session_id = self._client.session.create(behavior='release', ttl='10s')
        t = threading.Thread(target=self._keep_sessions_alive)
        t.daemon = True
        t.start()

    def _stop(self):
        """ """
        self._kill_flag.set()
        self._client.session.destroy(self._worker_session_id)
        self._client.session.destroy(self._task_session_id)

    def subscribe(self, on_task):
        cb = on_task or self.on_task
        try:
            while True:
                task = self._queue.get(self._task_session_id)
                if task:
                    try:
                        cb(task)
                        task.consume()
                    except Exception as exc:
                        logger.exception('Task failed')
                        task.cancel()
                logger.debug('Awaiting for further tasks...')
                time.sleep(1)
        except:
            if task and task.locked:
                task.cancel()
            self._stop()
            raise

    def on_task(self, task):
        """ """
        raise NotImplemented('No work required.')

    def _keep_sessions_alive(self):
        """ """
        while not self._kill_flag.isSet():
            for session_id in [self._worker_session_id, self._task_session_id]:
                resp = self._client.session.renew(session_id)
                logger.info('keep-alive sent: {}'.format(session_id))
            time.sleep(5)
        else:
            logger.warning('Keep alive stopped')


class Manager(Taskman):
    def __init__(self, vhost):
        logger.debug('Initialising a new manager...')
        super(Manager, self).__init__(vhost)

    def number_of_workers(self):
        workers = self._queue.list_workers()
        logger.info('{} workers found.'.format(len(workers)))

    def number_of_tasks(self):
        """ """
        tasks = list(self._queue._get_all_tasks())
        logger.info('{} tasks in total.'.format(len(tasks)))

    def number_of_queued_tasks(self):
        """ """
        tasks = list(self._queue._get_avaliable_tasks())
        logger.info('{} queued tasks.'.format(len(tasks)))

    def number_of_in_progress_tasks(self):
        """ """
        tasks = list(self._queue._get_locked_tasks())
        logger.info('{} currently in progress tasks.'.format(len(tasks)))


class Queue(object):

    _TASK_PREFIX = 'task_'
    _WORKER_PREFIX = 'worker_'
    _COUNTER_FILL = 10

    def __init__(self, client, base_path):
        """ """
        logger.debug('Initialising new queue - base_path:{}'.format(base_path))
        self._client = client
        self._base_path = base_path

        self._queue_path = posixpath.join(self._base_path, 'queue', '')
        self._workers_path = posixpath.join(self._base_path, 'workers', '')
        self._counter_path = posixpath.join(self._queue_path, 'counter')

        self._ensure_paths(self._queue_path, self._workers_path)
        self._setup_counter()

    def register_worker(self, session_id):
        """ """
        worker_name = '{}{}'.format(self._WORKER_PREFIX, session_id)
        path = posixpath.join(self._workers_path, worker_name)
        logger.debug('Registering worker: {}'.format(path))
        self._client.kv[path] = None
        self._client.kv.acquire_lock(item=path, session=session_id)

    def put(self, body, priority=100):
        """ """
        task_name = '{}{:03d}_{}'.format(self._TASK_PREFIX, priority, self._increment_counter())
        path = posixpath.join(self._queue_path, task_name)
        logger.debug('Adding new task: {}'.format(path))
        self._client.kv[path] = body

    def get(self, session_id):
        """ """
        for task in self._get_avaliable_tasks():
            if self._lock_key(path=task['Key'], session_id=session_id):
                return Task.from_consul_dict(queue=self, session_id=session_id, d=task)
            else:
                logging.error('Failed to lock task')

    def list_workers(self):
        """ """
        base_worker = posixpath.join(self._workers_path, self._WORKER_PREFIX)
        return self._get_children(base_worker)

    def cancel(self, task_path, session_id):
        """
        Cancel a task.

        This will release the lock on the task.
        """
        self._client.kv.release_lock(item=task_path, session=session_id)

    def consume(self, task_path, session_id):
        """ """
        if self._lock_key(task_path, session_id):
            logger.debug('Consuming task...')
            self._client.kv.delete(item=task_path)
        else:
            logger.warning('Task is locked by another worker.')
            raise RuntimeError('Task is locked by another worker')

    def _ensure_paths(self, *paths):
        """ """
        for path in paths:
            logger.debug('Ensuring path is available: {}'.format(path))
            if path not in self._client.kv:
                logger.debug('Creating path: {}'.format(path))
                self._client.kv[path] = None

    def _setup_counter(self):
        """ """
        logger.debug('Ensuring counter is available: {}'.format(self._counter_path))
        if self._counter_path not in self._client.kv:
            logger.debug('Creating counter: {}'.format(self._counter_path))
            self._client.kv[self._counter_path] = ''.zfill(self._COUNTER_FILL)

    def _get_avaliable_tasks(self):
        """
        Get all available tasks present in the queue.

        Any tasks that have been locked will not be returned. A locked task is determined if
        it has a session binded to it.
        """
        return (t for t in self._get_all_tasks() if not t.get('Session'))

    def _get_locked_tasks(self):
        """ """
        return (t for t in self._get_all_tasks() if t.get('Session'))

    def _get_all_tasks(self):
        """Get all tasks present in the queue."""
        base_task = posixpath.join(self._queue_path, self._TASK_PREFIX)
        available_tasks = self._get_children(base_task)
        return (task for task in available_tasks)

    def _get_children(self, path):
        """ """
        return self._client.kv._get_list(params=[path], query_params={'recurse': None})

    def _increment_counter(self):
        """Increment task counter and return the new count."""
        logger.debug('Getting counter value.')
        count = int(self._client.kv[self._counter_path])
        count += 1
        count_str = str(count).zfill(self._COUNTER_FILL)
        logger.debug('Incrementing counter to {}'.format(count_str))
        self._client.kv[self._counter_path] = count_str
        return count_str

    def _lock_key(self, path, session_id):
        """ """
        return self._client.kv.acquire_lock(path, session=session_id)




def send_task(args):
    """ """
    for i in range(args.repeat):
        client = Client(args.vhost)
        client.add_task(args.body, priority=args.priority)


def do_work(args):
    """ """
    def something(task):
        print('working on task...')
        # time.sleep(7)
        # if random.randint(0,2) == 1:
        #     print('transfer complete')
        # else:
        #     raise RuntimeError('transfer failed')

    worker = Worker(args.vhost)
    worker.subscribe(on_task=something)


def get_info(args):
    """ """
    manager = Manager(args.vhost)
    manager.number_of_workers()
    manager.number_of_tasks()
    manager.number_of_queued_tasks()
    manager.number_of_in_progress_tasks()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_client = subparsers.add_parser('client')
    parser_client.add_argument('--vhost')
    parser_client.add_argument('--body')
    parser_client.add_argument('--priority')
    parser_client.add_argument('--repeat', type=int, default=1)
    parser_client.set_defaults(func=send_task)

    parser_worker = subparsers.add_parser('worker')
    parser_worker.add_argument('--vhost')
    parser_worker.set_defaults(func=do_work)

    parser_manager = subparsers.add_parser('manager')
    parser_manager.add_argument('--vhost')
    parser_manager.set_defaults(func=get_info)

    arg = parser.parse_args()
    arg.func(arg)
