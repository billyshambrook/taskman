import time
import consulate
import taskman.worker
import sys


client = consulate.Consul()

w = taskman.worker.Worker(name=sys.argv[1], client=client, queue_name='myqueue')
w.start()

for m in w.subscribe():
    print('Got a task')
    time.sleep(20)
    m.consume()



#
# for x in range(15):
#     print(x)
#     time.sleep(1)
#
# w.stop()
#
# for i in range(15):
#     print(i)
