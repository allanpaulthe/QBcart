from .models import CartUser,Product,Cart,Order
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id','name', 'cost','photo', 'category')

class ProductDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id','name','description', 'cost','stock','photo','category','created_by')

class ProductCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('name','description', 'cost','stock','photo','category','created_by')

class CartCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cart
		fields = ('user','product', 'quantity','status','product_key')

class CartSerializer(serializers.ModelSerializer):
	class Meta:
		model = Cart
		fields = ('id','product', 'quantity','status')

class OrderCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ('user','product', 'quantity','status','price','order_date')

class OrderSerializer(serializers.ModelSerializer):
	class Meta:
		model = Order
		fields = ('id','product', 'quantity','status','price','order_date')