from celery import Celery

import sys, os, django
sys.path.append("/home/qburst/Documents/Projects/Django/qbcart/qbcart") #here store is root folder(means parent).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qbcart.settings")
django.setup()

from django.core.mail import EmailMessage
from django.template import loader, Context
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from basecart.models import Order,CartUser
from django_celery_beat.models import PeriodicTask,CrontabSchedule

app = Celery('tasks')
app.config_from_object('celeryconfig')

try:
	hourly_mail = PeriodicTask.objects.get(name='hourly_mail')
except PeriodicTask.DoesNotExist:
	period = CrontabSchedule.objects.get_or_create(minute='0',hour='*/1')
	hourly_mail = PeriodicTask(name='hourly_mail',task='tasks.send_hourly_email',crontab=period[0])
	hourly_mail.save()

def send_report_mail(orders_list,start,end):
	email_from = settings.EMAIL_HOST_USER
	subject="orders report"
	adminhtml = loader.get_template('email/hourlyreport.html')
	context = {'object_list':orders_list,'start':start,'end':end}
	html_content = adminhtml.render(context)
	adminmsg = EmailMessage(subject,html_content,email_from,[a[1] for a in settings.ADMINS])
	adminmsg.content_subtype = "html"
	adminmsg.send()

@app.task
def send_hourly_email():
	print("sending hourly report")
	end_time = timezone.now()
	start_time = end_time-timedelta(hours=1)
	print("between:")
	print('start:'+str(start_time))
	print('end:'+str(end_time))
	products_ordered_in_past_hour=Order.objects.filter(order_date__gte=start_time,order_date__lte=end_time)
	send_report_mail(products_ordered_in_past_hour,start_time,end_time)

@app.task
def send_confirmation_email(id,orders):
	order_list = Order.objects.filter(id__in=orders)
	user=CartUser.objects.get(id=id)
	email_from = settings.EMAIL_HOST_USER
	recipient_list = [user.email]
	subject='order placed'

	buyerhtml = loader.get_template('email/orderconfirmation.html')
	context = {'username':user.username,'object_list':order_list}
	html_content = buyerhtml.render(context)
	buyermsg = EmailMessage(subject,html_content,email_from,recipient_list)
	buyermsg.content_subtype = "html"
	
	adminhtml = loader.get_template('email/responsetoadmin.html')
	context = {'username':user.username,'object_list':order_list}
	html_content = adminhtml.render(context)
	adminmsg = EmailMessage(subject,html_content,email_from,[a[1] for a in settings.ADMINS])
	adminmsg.content_subtype = "html"

	buyermsg.send()
	adminmsg.send()

	sellers = [order.product.created_by.id for order in order_list]
	sellers = set(sellers)
	for seller in sellers:
		seller_orders = Order.objects.filter(id__in=orders,product__created_by__id=seller)
		seller_detail = CartUser.objects.get(id=seller)
		sellerhtml = loader.get_template('email/responsetoseller.html')
		context = {'username':user.username,'orders_list':seller_orders,'seller':seller_detail.username}
		html_content = sellerhtml.render(context)
		sellermsg = EmailMessage(subject,html_content,email_from,[seller_detail.email])
		sellermsg.content_subtype = "html"
		sellermsg.send()