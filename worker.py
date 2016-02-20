


worker = Worker('192.168.99.100', 32828, 'taskman/queue')

for task in worker.subscribe():
    time.sleep(2)
    # print(json.loads(task))
