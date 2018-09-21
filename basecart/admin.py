from django.contrib import admin
from .models import CartUser,Product,Cart,Order,CartActivityLogger

# Register your models here.
class CartUserAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,               {'fields': ['username']}),
		('Name',{'fields':['first_name','last_name']}),
		('Role', {'fields': ['role']}),
		('Email',{'fields':['email']}),
		('Address',{'fields':['address']}),
	]
	list_display = ('username', 'email', 'role')
	list_filter=['username']
	ordering=['username']
	search_fields = ['username']

admin.site.register(CartUser,CartUserAdmin)

class ProductAdmin(admin.ModelAdmin):
	fieldsets=[
	(None, {'fields':['name']}),
	('Details',{'fields':['description','cost','stock','category', 'created_by']}),
	('Photo',{'fields':['photo']})
	]
	list_display = ('name', 'cost', 'stock')
	list_filter=['category']
	ordering=['name']
	search_fields = ['name']

admin.site.register(Product,ProductAdmin)

class CartAdmin(admin.ModelAdmin):
	fieldsets=[
	(None, {'fields':['user']}),
	('Products',{'fields':['product']})
	]
	list_display = ('user', 'product','status')

admin.site.register(Cart,CartAdmin)

class OrderAdmin(admin.ModelAdmin):
	fieldsets=[
	(None, {'fields':['user']}),
	('Products',{'fields':['product']})
	]
	list_display = ('user', 'product', 'order_date','status')

admin.site.register(Order,OrderAdmin)

class CartLoggerAdmin(admin.ModelAdmin):
	fieldsets=[
	('Data',{'fields':['product']})
	]
	list_display = ('username','email','action', 'product', 'date_and_time','comments')

admin.site.register(CartActivityLogger,CartLoggerAdmin)