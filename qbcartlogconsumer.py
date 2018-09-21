import pika
import json
import sys, os, django
sys.path.append("/home/qburst/Documents/Projects/Django/qbcart/qbcart") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qbcart.settings")
django.setup()

from basecart.models import CartActivityLogger

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='qbcartlog')

def callback(ch, method, properties, body):
	print(type(body))
	my_data = body.decode('utf8')
	data = json.loads(my_data)
	print(data)
	log=CartActivityLogger(
		username=data['user'],
		email=data['email'],
		product=data['product'],
		comments=data['comments'],
		date_and_time=data['date_time'],
		action=data['action']
		)
	log.save()

channel.basic_consume(callback,
					queue='qbcartlog',
					no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
