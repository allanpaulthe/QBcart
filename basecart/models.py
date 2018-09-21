from django.db import models
from django.contrib.auth.models import AbstractUser
import random

# Create your models here.
class CartUser(AbstractUser):
	Buyer='BY'
	Seller='SL'

	ROLES=(
		(Buyer,'Buyer'),
		(Seller,'Seller'),
		)
	role=models.CharField(max_length=2, choices=ROLES, default=Buyer)
	address=models.TextField(blank=True)

	def __str__(self):
		return self.username

class Product(models.Model):
	Electronics=1
	Fasion=2
	Home=3
	Toys=4
	Books=5
	CATEGORIES=(
		(Electronics,'Electronics'),
		(Fasion,'Fasion'),
		(Home,'Home'),
		(Toys,'Toys'),
		(Books,'Books'),
		)
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	cost = models.PositiveIntegerField()
	stock = models.PositiveIntegerField()
	photo = models.ImageField(upload_to='productimage')
	category = models.IntegerField(choices=CATEGORIES, default=Electronics)
	created_by = models.ForeignKey(CartUser, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

	def set_product_key(self):
		return random.randint(1,101)

class Cart(models.Model):
	Incart = 'IC'
	Inorder = 'IO'
	STATUSES = (
		(Incart,'Incart'),
		(Inorder,'Inorder'),
		)
	user = models.ForeignKey(CartUser, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	status = models.CharField(max_length=2, choices=STATUSES, default=Inorder)
	product_key = models.PositiveIntegerField(default=0) 
	
	def __str__(self):
		return self.product.name

class Order(models.Model):
	Placed = 'PL'
	Notplaced = 'NP'
	Cancelled = 'CN'
	STATUSES=(
		(Placed,'Placed'),
		(Notplaced,'Notplaced'),
		(Cancelled, 'Cancelled')
		)
	user = models.ForeignKey(CartUser, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	order_date = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=2, choices=STATUSES, default= Notplaced)
	quantity = models.PositiveIntegerField(default=1)
	price = models.PositiveIntegerField(default=0)
	
	def __str__(self):
		return self.user.username

class CartActivityLogger(models.Model):
	Productcreated ='PC'
	Productupdated ='PU'
	Productdeleted = 'PD'
	Addedtocart = 'AC'
	Removedfromcart ='RC'
	Movedtowishlist = 'MW'
	Updatedcart = 'UC'
	Ordercreated = 'OR'
	Orderplaced = 'OP'
	Ordercancelled ='OC'

	ACTIONS = (
		(Productcreated,'Product Created'),
		(Productupdated,'Product Updated'),
		(Productdeleted,'Product Deleted'),
		(Addedtocart,'Added to Cart'),
		(Updatedcart,'Updated Cart'),
		(Removedfromcart,'Removed from Cart'),
		(Movedtowishlist,'Moved to Wishlist'),
		(Ordercreated,'Order Created'),
		(Orderplaced,'Order Placed'),
		(Ordercancelled,'Order Cancelled'),
	)

	username = models.CharField(max_length = 100)
	email = models.CharField(max_length = 200)
	action = models.CharField(max_length =2, choices=ACTIONS)
	product = models.CharField(max_length = 100)
	comments = models.TextField(blank=True)
	date_and_time = models.CharField(max_length = 100)

	def __str__(self):
		return self.username