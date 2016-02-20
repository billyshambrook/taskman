import posixpath
import pytest
import uuid

import consulate

import taskman.queue


@pytest.fixture(scope="session")
def client():
    return consulate.Consul()


@pytest.fixture
def queue(request, client):
    path = uuid.uuid4().hex
    queue = taskman.queue.Queue(client, path)
    def fin():
        client.kv.delete(path, recurse=True)
    request.addfinalizer(fin)
    return queue


class TestQueue(object):

    def test_initial_counter(self, queue):
        """Ensure counter is set correctly when first creating queue."""
        assert queue._counter == '0000000001'

    def test_empty_queue(self, queue):
        """Ensure methods work when the queue is empty."""
        assert len(queue) == 0
        assert not queue.get()
        assert len(queue) == 0

    def test_queue(self, queue):
        """Ensure you can put stuff on the queue and get it back."""
        queue.put('foo')
        queue.put('bar')
        queue.put('dar')
        assert len(queue) == 3

        assert queue.get() == 'foo'
        assert queue.get() == 'bar'
        assert queue.get() == 'dar'
        assert len(queue) == 0

    def test_priority(self, queue):
        """Ensure tasks are given back in order of priority."""
        queue.put('foo')
        queue.put('bar', priority=30)
        queue.put('dar', priority=100)

        assert queue.get() == 'bar'
        assert queue.get() == 'foo'
        assert queue.get() == 'dar'
