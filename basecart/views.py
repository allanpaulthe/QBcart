from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView,DetailView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import CartUser,Product,Cart,Order,CartActivityLogger
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from .qbcartlogger import logdata
import json
from rest_framework import viewsets
from .serializers import (
	ProductDetailSerializer,
	ProductSerializer,
	ProductCreateSerializer,
	CartCreateSerializer,
	CartSerializer,
	OrderCreateSerializer,
	OrderSerializer,
	)
from rest_framework import status,permissions
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.http import Http404
from rest_framework.generics import GenericAPIView
from tasks import send_confirmation_email
from django_celery_beat.models import CrontabSchedule, PeriodicTask

# Create your views here.
# API section
@csrf_exempt
@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
def login(request):
	"""
		Returns user auth token
		---
		# Parameters:
			{
				"username":"string",
				"password":"string"
			}
		# Response:
			200:
				{
					"data": {
						"token": "string"
					},
					"status": "ok",
					"error": ""
				}
		"""
	username = request.data.get("username")
	password = request.data.get("password")
	if username is None or password is None:
		return Response({'error':'Please provide both username and password','status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	user = authenticate(username=username, password=password)
	if not user:
		return Response({'error': 'Invalid Credentials','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)

	token, _ = Token.objects.get_or_create(user=user)
	return Response({'data':{'token': token.key},'status':'ok','error': ''},status=status.HTTP_200_OK)

#products
@permission_classes((permissions.IsAuthenticatedOrReadOnly,))
class ProductDetail(GenericAPIView):

	serializer_class = ProductCreateSerializer
	def get(self, request, pk, *args, **kwargs):
		"""
		Returns product details
		---
		# Parameters:
			id:
				required:True
				type:Integer
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"name": "string",
						"description": "text",
						"cost": integer,
						"stock": integer,
						"photo": "string",
						"category": integer,
						"created_by": integer
						},
					"status": "ok",
					"error": ""
				}

		"""
		try:
			product = Product.objects.get(pk=pk)
		except Product.DoesNotExist:
			return Response({'error':'product does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		serializer = ProductDetailSerializer(product)
		return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def put(self, request, pk, *args, **kwargs):
		"""
		updates product details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body:
				{
					"created_by": 0,
					"stock": 0,
					"name": "string",
					"photo": "string",
					"category": "string",
					"description": "string",
					"cost": 0
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"name": "string",
						"description": "text",
						"cost": integer,
						"stock": integer,
						"photo": "string",
						"category": integer,
						"created_by": integer
						},
					"status": "ok",
					"error": ""
				}

		"""
		try:
			product = Product.objects.get(pk=pk)
		except Product.DoesNotExist:
			return Response({'error':'product does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		serializer = ProductDetailSerializer(product, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, pk, *args, **kwargs):
		"""
		updates particular product details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body:
				{
					"created_by": 0,
					"stock": 0,
					"name": "string",
					"photo": "string",
					"category": "string",
					"description": "string",
					"cost": 0
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"name": "string",
						"description": "text",
						"cost": integer,
						"stock": integer,
						"photo": "string",
						"category": integer,
						"created_by": integer
						},
					"status": "ok",
					"error": ""
				}

		"""
		try:
			product = Product.objects.get(pk=pk)
		except Product.DoesNotExist:
			return Response({'error':'product does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		serializer = ProductDetailSerializer(product, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, *args, **kwargs):
		"""
		Deletes product
		---
		# Parameters:
			id:
				required:True
				type:Integer
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"name": "string",
						"description": "text",
						"cost": integer,
						"stock": integer,
						"photo": "string",
						"category": integer,
						"created_by": integer
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			product = Product.objects.get(pk=pk)
		except Product.DoesNotExist:
			return Response({'error':'product does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		serializer = ProductDetailSerializer(product)
		product.delete()
		return Response({'data':serializer.data, 'status':'ok','error':''},status=status.HTTP_200_OK)

@permission_classes((permissions.IsAuthenticatedOrReadOnly,))
class ProductListOrCreate(GenericAPIView):
	serializer_class = ProductCreateSerializer

	def get(self, request, *args, **kwargs):
		"""
		lists all products
		---
		# Parameters:
			None
		# Response:
			200:
				{
					"data": 
						[
							{
								"id": integer,
								"name": "string",
								"cost": integer,
								"photo": "string",
								"category": integer,
							},
						]
					"status": "ok",
					"error": ""
				}

	"""
		try:
			products = Product.objects.all()
		except Product.DoesNotExist:
			return Response({'error':'products list empty','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)	
		
		serializer = ProductSerializer(products, many=True)
		return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		"""
		Creates new product
		---
		# Parameters:
			{
				"cost": 0,
				"photo": "string",
				"description": "string",
				"name": "string",
				"category": "string",
				"created_by": 0,
				"stock": 0
			}
		# Response:
			200:
				{
					"data":
						{
							"id": integer,
							"name": "string",
							"cost": integer,
							"photo": "string",
							"category": integer,
						},
					"status": "ok",
					"error": ""
				}

		"""
		serializer = ProductCreateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

#cart

@permission_classes((permissions.IsAuthenticated,))
class CartDetail(GenericAPIView):

	serializer_class = CartSerializer

	def get(self, request, pk, *args, **kwargs):
		print('in get')
		"""
		returns cart details
		---
		# Parameters:
			id:
				required:True
				type:Integer
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string"
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			cart = Cart.objects.get(pk=pk)
			print(cart)
		except Cart.DoesNotExist:
			return Response({'error':'cart item does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = CartSerializer(cart)
		return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def put(self, request, pk, *args, **kwargs):
		"""
		updates cart details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body:
				{
					"id": integer,
					"product": integer,
					"quantity": integer,
					"status": "string"
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string"
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			cart = Cart.objects.get(pk=pk)
		except Cart.DoesNotExist:
			return Response({'error':'cart item does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = CartSerializer(cart, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, pk, *args, **kwargs):
		"""
		updates specific cart details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body:
				{
					"id": integer,
					"product": integer,
					"quantity": integer,
					"status": "string"
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string"
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			cart = Cart.objects.get(pk=pk)
		except Cart.DoesNotExist:
			return Response({'error':'cart item does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = CartSerializer(cart, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, *args, **kwargs):
		"""
		deletes cart entry
		---
		# Parameters:
			id:
				required:True
				type:Integer
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string"
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			cart = Cart.objects.get(pk=pk)
		except Cart.DoesNotExist:
			return Response({'error':'cart item does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = CartSerializer(cart)
		product.delete()
		return Response({'data':serializer.data, 'status':'ok','error':''},status=status.HTTP_200_OK)

@permission_classes((permissions.IsAuthenticated,))
class CartListOrCreate(GenericAPIView):
	serializer_class = CartCreateSerializer
	def get(self, request, *args, **kwargs):
		"""
		Lists all Cart entries
		---
		# Parameters:
			None
		# Response:
			200:
				{
					"data":
						{
							"id": integer,
							"product": integer,
							"quantity": integer,
							"status": "string",
						},
					"status": "ok",
					"error": ""
				}

		"""
		try:
			cart = Cart.objects.all()
		except Cart.DoesNotExist:
			return Response({'error':'cart empty','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		if not cart:
			return Response({'error':'cart empty','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		else:
			serializer = CartSerializer(cart, many=True)
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		"""
		Creates new cart entry
		---
		# Parameters:
			{
				"product_key": integer,
				"quantity": integer,
				"status": "string",
				"product": integer,
				"user": integer
			}
		# Response:
			200:
				{
					"data":
						{
							"id": integer,
							"product": integer,
							"quantity": integer,
							"status": "string",
						},
					"status": "ok",
					"error": ""
				}

		"""
		serializer = CartCreateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

#order
@permission_classes((permissions.IsAuthenticated,))
class OrderDetail(GenericAPIView):
	serializer_class = OrderSerializer
	
	def get(self, request, pk, *args, **kwargs):
		"""
		returns order details
		---
		# Parameters:
			id:
				required:True
				type:Integer
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			order = Order.objects.get(pk=pk)
		except Order.DoesNotExist:
			return Response({'error':'order does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = OrderSerializer(order)
		return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def put(self, request, pk, *args, **kwargs):
		"""
		updates order details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body: 
				{
					"id": integer,
					"product": integer,
					"quantity": integer,
					"status": "string",
					"price": integer,
					"order_date": datetime
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			order = Order.objects.get(pk=pk)
		except Order.DoesNotExist:
			return Response({'error':'order does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = OrderSerializer(order, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def patch(self, request, pk, *args, **kwargs):
		"""
		updates specific order details
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body: 
				{
					"id": integer,
					"product": integer,
					"quantity": integer,
					"status": "string",
					"price": integer,
					"order_date": datetime
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			order = Order.objects.get(pk=pk)
		except Order.DoesNotExist:
			return Response({'error':'order does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = OrderSerializer(order, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk, *args, **kwargs):
		"""
		deletes order
		---
		# Parameters:
			id:
				required:True
				type:Integer
			body: 
				{
					"id": integer,
					"product": integer,
					"quantity": integer,
					"status": "string",
					"price": integer,
					"order_date": datetime
				}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}
		"""
		try:
			order = Order.objects.get(pk=pk)
		except Order.DoesNotExist:
			return Response({'error':'order does not exist','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = OrderSerializer(order)
		product.delete()
		return Response({'data':serializer.data, 'status':'ok','error':''},status=status.HTTP_200_OK)

@permission_classes((permissions.IsAuthenticated,))
class OrderListOrCreate(GenericAPIView):
	serializer_class = OrderCreateSerializer
	
	def get(self, request, *args, **kwargs):
		"""
		returns all orders
		---
		# Parameters:
			None
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}

		"""
		try:
			order = Order.objects.all()
		except Order.DoesNotExist:
			return Response({'error':'order empty','status':'fail','data':''},status=status.HTTP_404_NOT_FOUND)
		
		serializer = OrderSerializer(order, many=True)
		return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		"""
		Creates new order
		---
		# Parameters:
			{
				"price": integer,
				"quantity": integer,
				"status": "string",
				"product": integer,
				"user": integer
			}
		# Response:
			200:
				{
					"data": {
						"id": integer,
						"product": integer,
						"quantity": integer,
						"status": "string",
						"price": integer,
						"order_date": datetime
						},
					"status": "ok",
					"error": ""
				}

		"""
		serializer = OrderCreateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response({'data':serializer.data,'status':'ok','error':''},status=status.HTTP_200_OK)
		return Response({'error':serializer.errors,'status':'fail','data':''},status=status.HTTP_400_BAD_REQUEST)

# json creator
def create_json(user,action,product,comments):
	data={}
	data['user']=user.username
	data['email']=user.email
	data['action']=action
	data['product']=product
	data['comments']=comments
	data['date_time']=timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
	json_data=json.dumps(data)
	print(json_data)
	return json_data

# basecart functions

#product based methods
def delete_product(self):
	if(self.request.method == 'GET' and self.request.GET.get('delete')):
		productid = self.request.GET.get('delete')
		try:
			name = Product.objects.get(id=productid).name
			Product.objects.get(id=productid).delete()
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Productdeleted,
				product=name,
				comments='product deleted')
			logdata(json_data)
		except Product.DoesNotExist:
			pass
#cart based methods
def delete_cart_entry(self):
	if(self.request.method == 'GET' and self.request.GET.get('delcart')):
		productid = self.request.GET.get('delcart')
		try:
			cart = Cart.objects.get(id=productid)
			Cart.objects.get(id=productid).delete()
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Removedfromcart,
				product=cart.product.name,
				comments='delete from cart')
			logdata(json_data)
		except Cart.DoesNotExist:
			pass

def add_cart_entry(self):
	if(self.request.method == 'GET' and self.request.GET.get('addcart')):
		productid = self.request.GET.get('addcart')
		qty = self.request.GET.get('qty')
		key = int(self.request.GET.get('key'))
		try:
			cart_item = Product.objects.get(pk=productid)
			user_detail = CartUser.objects.get(id=self.request.user.id)
			if(check_if_cart_exist_or_new(cart_item,user_detail,key)==0):
				json_data=create_json(
					user=CartUser.objects.get(id=self.request.user.id),
					action=CartActivityLogger.Addedtocart,
					product=cart_item.name,
					comments='added to cart')
				logdata(json_data)
				new_cart_entry=Cart( user=user_detail, product=cart_item, quantity=qty, product_key=key)
				new_cart_entry.save()
			else:
				Cart.objects.filter(user=user_detail, product=cart_item).update(status=Cart.Inorder)
				json_data=create_json(
					user=CartUser.objects.get(id=self.request.user.id),
					action=CartActivityLogger.Movedtowishlist,
					product=cart_item.name,
					comments='moved to cart')
				logdata(json_data)

		except Product.DoesNotExist:
			pass	

def check_if_cart_exist_or_new(cart_item,user_detail,key):
	try:
		Cart.objects.get(user=user_detail, product=cart_item)
		return 1
	except Cart.DoesNotExist:
		print('cart does not exist')
		return 0

def update_cart_entry(self):
	if(self.request.method == 'GET' and self.request.GET.get('qty')):
		qty=int(self.request.GET.get('qty'))
		cartid=self.request.GET.get('id')
		Cart.objects.filter(id=cartid).update(quantity=qty)
		cart_item = Cart.objects.get(id=cartid)
		json_data=create_json(
			user=CartUser.objects.get(id=self.request.user.id),
			action=CartActivityLogger.Updatedcart,
			product=cart_item.product.name,
			comments='updated quantity = '+str(cart_item.quantity))
		logdata(json_data)

def update_cart_status(self):
	if(self.request.method == 'GET' and self.request.GET.get('status')):
		cartid=self.request.GET.get('id')
		if(self.request.GET.get('status') == '1'):
			cart_item=Cart.objects.get(id=cartid)
			Cart.objects.filter(id=cartid).update(status=Cart.Incart)
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Movedtowishlist,
				product=cart_item.product.name,
				comments='moved to wishlist')
			logdata(json_data)
		else:
			cart_item=Cart.objects.get(id=cartid)
			Cart.objects.filter(id=cartid).update(status=Cart.Inorder)
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Movedtowishlist,
				product=cart_item.product.name,
				comments='moved from wishlist to cart')
			logdata(json_data)

#order based methods
def create_order(self):
	if(self.request.method == 'GET' and self.request.GET.get('checkout')):
		userid = self.request.GET.get('checkout')
		user = CartUser.objects.get(id=userid)
		cart_items = Cart.objects.filter(user=user,status=Cart.Inorder)
		for product in cart_items:
			cart = Cart.objects.get(id=product.id, status = Cart.Inorder)
			if(check_if_order_exist_or_new(cart,user)==1):
				order_product = Product.objects.get(id=cart.product.id)
				Order.objects.filter(user=user, product=cart.product, status=Order.Notplaced).update(quantity=cart.quantity, price=cart.quantity*order_product.cost)
			else:
				new_product = Product.objects.get(id=cart.product.id)
				new_order = Order(user=user, product=new_product, quantity=cart.quantity, price=cart.quantity*new_product.cost)
				new_order.save()
				json_data=create_json(
					user=CartUser.objects.get(id=self.request.user.id),
					action=CartActivityLogger.Ordercreated,
					product=new_product.name,
					comments='order created quantity='+str(cart.quantity))
				logdata(json_data)

def check_if_order_exist_or_new(cart_item,user_detail):
	try:
		Order.objects.get(user=user_detail, product=cart_item.product, status=Order.Notplaced)
		orderid = Order.objects.filter(user=user_detail, product=cart_item.product).order_by('-order_date')[0]
		order = Order.objects.get(id=orderid.id)
		if(order.status!=Order.Notplaced):
			return 0
		else:
			return 1
	except Order.DoesNotExist:
		return 0

def delete_order(self):
	if(self.request.method == 'GET' and self.request.GET.get('delorder')):
		orderid = self.request.GET.get('delorder')
		try:
			order = Order.objects.get(id=orderid)
			product = Product.objects.get(id=order.product.id)
			user = CartUser.objects.get(id=self.request.user.id)
			Order.objects.get(id=orderid).delete()
			Cart.objects.filter(user=user,product=product).update(status=Cart.Incart)
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Movedtowishlist,
				product=product.name,
				comments='order deleted and moved to wishlist')
			logdata(json_data)
		except Order.DoesNotExist:
			pass
def add_address(self):
	if(self.request.method == 'GET' and self.request.GET.get('address')):
		address = self.request.GET.get('address')
		CartUser.objects.filter(id=self.request.user.id).update(address=address)

def deliver_order(self):
	if(self.request.method == 'GET' and self.request.GET.get('deliver')):
		userid=self.request.GET.get('deliver')
		user=CartUser.objects.get(id=userid)
		order_list = [order.id for order in Order.objects.filter(user=user,status=Order.Notplaced)]
		send_confirmation_email.delay(id=user.id,orders=order_list)
		for orders in Order.objects.filter(user=user,status=Order.Notplaced):
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Orderplaced,
				product=orders.product.name,
				comments='delivery initiated quantity='+str(orders.quantity))
			logdata(json_data)
		Order.objects.filter(user=user,status=Order.Notplaced).update(status=Order.Placed)
		Cart.objects.filter(user=user, status=Cart.Inorder).delete()

def cancel_order(self):
	if(self.request.method == 'GET' and self.request.GET.get('cancel')):
		orderid = self.request.GET.get('cancel')
		try:
			Order.objects.filter(id=orderid).update(status=Order.Cancelled)
			order=Order.objects.get(id=orderid)
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Ordercancelled,
				product=order.product.name,
				comments='order cancelled')
			logdata(json_data)
		except Order.DoesNotExist:
			pass

def remove_cancelled_order(self):
	if(self.request.method == 'GET' and self.request.GET.get('remove')):
		orderid = self.request.GET.get('remove')
		try:
			order=Order.objects.get(id=orderid)
			Order.objects.get(id=orderid).delete()
			json_data=create_json(
				user=CartUser.objects.get(id=self.request.user.id),
				action=CartActivityLogger.Ordercancelled,
				product=order.product.name,
				comments='removed from orderslist')
			logdata(json_data)
		except Order.DoesNotExist:
			pass

class IndexView(ListView):
	template_name = 'basecart/index.html'
	model = Product

	def get_queryset(self):
		if(self.request.user.is_authenticated):
			add_cart_entry(self)
			delete_product(self)
		return Product.objects.all()

#user class features
class CartUserCreationForm(UserCreationForm):
	class Meta:
		model = CartUser
		fields = UserCreationForm.Meta.fields + ('email','role',)

class SignUpView(CreateView):
	form_class = CartUserCreationForm
	template_name = 'registration/signup.html'
	success_url = reverse_lazy('login')

# Product class features
class AddProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = ['name', 'description', 'photo', 'category', 'cost', 'stock']

class AddProductView(CreateView):
	form_class = AddProductForm
	template_name = 'basecart/addproduct.html'
	success_url = reverse_lazy('index')

	def form_valid(self,form):
		if(self.request.user.is_authenticated):
			userid=self.request.user.id
			self.object = form.save(commit=False)
			product_photo=form.cleaned_data['photo']
			self.object.created_by = CartUser.objects.get(id=userid)
			self.object.photo = product_photo
			self.object.save()
			json_data=create_json(
				user=CartUser.objects.get(id=userid),
				action=CartActivityLogger.Productcreated,
				product=form.cleaned_data['name'],
				comments='cost='+str(form.cleaned_data['cost']))
			logdata(json_data)
			return super(AddProductView, self).form_valid(form)

class ProductDetailView(DetailView):
	model = Product
	template_name = 'basecart/productdetail.html'

class ProductEditView(UpdateView):
	model = Product
	template_name = 'basecart/productedit.html'
	fields = ['name','description','cost','stock']
	success_url = reverse_lazy('index')
	def form_valid(self,form):
		if(self.request.user.is_authenticated):
			userid=self.request.user.id
			json_data=create_json(
				user=CartUser.objects.get(id=userid),
				action=CartActivityLogger.Productupdated,
				product=form.cleaned_data['name'],
				comments='NULL')
			logdata(json_data)
			return super(ProductEditView, self).form_valid(form)

class MyProductsView(ListView):
	model = Product
	template_name = 'basecart/myproducts.html'
	def get_queryset(self):
		if(self.request.user.is_authenticated):
			return Product.objects.filter(created_by=self.request.user)

# Cart class features
class CartDetailView(ListView):
	model = Cart
	template_name = 'basecart/cart.html'

	def get_queryset(self):
		if(self.request.user.is_authenticated):
			delete_cart_entry(self)
			update_cart_entry(self)
			update_cart_status(self)
		return Cart.objects.filter(user=self.request.user)

# Order class features
class CreateOrder(ListView):
	model = Order
	template_name = 'basecart/placeorder.html'
	def get_queryset(self):
		if(self.request.user.is_authenticated):
			create_order(self)
			delete_order(self)
			add_address(self)
		return Order.objects.filter(user=self.request.user, status=Order.Notplaced)	

class ViewOrder(ListView):
	model = Order
	template_name = 'basecart/vieworder.html'
	def get_queryset(self):
		deliver_order(self)
		cancel_order(self)
		remove_cancelled_order(self)
		return Order.objects.filter(user=self.request.user).order_by('-order_date')

# admin page
def delete_cartuser(self):
	if(self.request.method == 'GET' and self.request.GET.get('deluser')):
		userid = self.request.GET.get('deluser')
		try:
			CartUser.objects.get(id=userid).delete()
		except CartUser.DoesNotExist:
			pass

def delete_log(self):
	if(self.request.method == 'GET' and self.request.GET.get('dellog')):
		logid = self.request.GET.get('dellog')
		try:
			CartActivityLogger.objects.get(id=logid).delete()
		except CartActivityLogger.DoesNotExist:
			pass
## CartUserAdmin classes
class CartUserAdmin(ListView):
	model = CartUser
	template_name = 'administration/user/cartuseradmin.html'
	def get_queryset(self):
		delete_cartuser(self)
		return CartUser.objects.all()

class CartUserEditAdmin(UpdateView):
	model = CartUser
	template_name = 'administration/user/cartusereditadmin.html'
	fields = ['username','first_name','last_name','email','role','address']
	success_url = reverse_lazy('cartuseradmin')

class CartUserCreateAdmin(CreateView):
	model = CartUser
	fields = ['username','first_name','last_name','email','role','address']
	template_name = 'administration/user/cartusercreateadmin.html'
	success_url = reverse_lazy('cartuseradmin')

## ProductAdmin classes
class ProductAdmin(ListView):
	model = Product
	template_name = 'administration/product/productadmin.html'
	def get_queryset(self):
		delete_product(self)
		return Product.objects.all()

class ProductEditAdmin(UpdateView):
	model = Product
	template_name = 'administration/product/producteditadmin.html'
	fields = ['name','description','photo','cost','stock','category','created_by']
	success_url = reverse_lazy('productadmin')

class ProductCreateAdmin(CreateView):
	model = Product
	fields = ['name','description','photo','cost','stock','category','created_by']
	template_name = 'administration/product/createproductadmin.html'
	success_url = reverse_lazy('productadmin')

## CartAdmin classes
class CartAdmin(ListView):
	model = Cart
	template_name = 'administration/cart/cartadmin.html'
	def get_queryset(self):
		delete_cart_entry(self)
		return Cart.objects.all()

class CartEditAdmin(UpdateView):
	model = Cart
	template_name = 'administration/cart/carteditadmin.html'
	fields = ['user','product','quantity','product_key','status']
	success_url = reverse_lazy('cartadmin')

class CartCreateAdmin(CreateView):
	model = Cart
	fields = ['user','product','quantity','product_key','status']
	template_name = 'administration/cart/cartcreateadmin.html'
	success_url = reverse_lazy('cartadmin')

## OrderAdmin classes
class OrderAdmin(ListView):
	model = Order
	template_name = 'administration/order/orderadmin.html'
	def get_queryset(self):
		remove_cancelled_order(self)
		return Order.objects.all()

class OrderEditAdmin(UpdateView):
	model = Order
	template_name = 'administration/order/ordereditadmin.html'
	fields = ['user','product','quantity','status','price']
	success_url = reverse_lazy('orderadmin')

class OrderCreateAdmin(CreateView):
	model = Order
	fields = ['user','product','quantity','status','price']
	template_name = 'administration/order/ordercreateadmin.html'
	success_url = reverse_lazy('orderadmin')

## CartActivityLoggerAdmin classes
class CartActivityLoggerAdmin(ListView):
	model = CartActivityLogger
	template_name = 'administration/activity/cartactivityloggeradmin.html'
	def get_queryset(self):
		delete_log(self)
		return CartActivityLogger.objects.all().order_by('-date_and_time')

class CartActivityLoggerEditAdmin(UpdateView):
	model = CartActivityLogger
	template_name = 'administration/activity/cartactivityloggereditadmin.html'
	fields = ['username','email','action','product','comments','date_and_time']
	success_url = reverse_lazy('orderadmin')

class CartActivityLoggerCreateAdmin(CreateView):
	model = CartActivityLogger
	fields = ['username','email','action','product','comments','date_and_time']
	template_name = 'administration/activity/cartactivityloggercreateadmin.html'
	success_url = reverse_lazy('orderadmin')

class PeriodAdmin(ListView):
	model = PeriodicTask
	template_name = 'administration/period/periodadmin.html'
	def get_queryset(self):
		return PeriodicTask.objects.exclude(name__startswith='celery')

class PeriodEditAdmin(UpdateView):
	model = CrontabSchedule
	template_name = 'administration/period/setperiod.html'
	fields = ['minute','hour','day_of_week','day_of_month','month_of_year']
	success_url = reverse_lazy('viewperiod')