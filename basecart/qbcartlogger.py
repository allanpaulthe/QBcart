import pika

def logdata(message):
	print('hello')
	connection=pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel= connection.channel()

	channel.queue_declare(queue='qbcartlog')
	channel.basic_publish(exchange='',
		routing_key='qbcartlog',
		body=message)

	print('[x] Sent'+ message)
	connection.close()
