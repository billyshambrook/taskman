client = Client(host='192.168.99.100', port=32828, queue_path='taskman/queue')
client.put({'hello': 'world'}, priority=sys.argv[1])
