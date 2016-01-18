Getting started
===============

Consul client
-------------

`taskman` uses the python consul api wrapper library `consulate`. To use most of the features of `taskman`, you first
need to create a `consulate` client like so:

.. code-block:: python

  >>> import consulate
  >>> client = consulate.Consul()

You can find information on what arguments you can pass to the client
`here <https://consulate.readthedocs.org/en/stable/consul.html#consulate.Consul>`_.


Queue
-----

First you need create a queue:

.. code-block:: python

  >>> import taskman.queue
  >>> myqueue = taskman.queue.Queue(client, path='/myqueue')

`taskman` will start setting up the correct key structure for the queue in the path given to it.

You can check the length of the queue with:

  >>> len(myqueue)
  0

You can put a task on the queue using the `put` method. The task body must be a string.

  >>> myqueue.put('hello, world')
  >>> len(myqueue)
  1

You can also give the task a priority. The priority is a integer value, with at most 3 digits. Lower values signify
a higher priority. The default is 100, so if you want to make the next task a higher priority, you can do:

  >>> myqueue.put('foo bar', priority=10)

To pick a task off the queue you do:

  >>> task = myqueue.get()
  >>> task
  'foo bar'

This will remove the task from the queue:

  >>> len(myqueue)
  1
