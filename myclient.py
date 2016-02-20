import consulate
import taskman.worker


client = consulate.Consul()

# w = taskman.worker.Worker(name='myworker', client=client, queue_name='myqueue')

q = taskman.queue.Queue(client=client, base_path='queues/myqueue', session_id='hello')
q.put('hello')

#
# for x in range(15):
#     print(x)
#     time.sleep(1)
#
# w.stop()
#
# for i in range(15):
#     print(i)
