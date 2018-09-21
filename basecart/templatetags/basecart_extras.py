from django import template
from ..models import CartUser,Cart,Order

# template tags
register = template.Library()

@register.simple_tag
def multiply(qty, price):
    return qty*price

@register.simple_tag
def items_in_cart(userid):
	count = 0
	try:
		user = CartUser.objects.get(id=userid)
		count = len(Cart.objects.filter(user=user,status=Cart.Inorder))
	except CartUser.DoesNotExist:
		pass
	return count

@register.simple_tag
def items_in_order(userid):
	count = 0
	try:
		user = CartUser.objects.get(id=userid)
		count = len(Order.objects.filter(user=user,status=Order.Notplaced))
	except CartUser.DoesNotExist:
		pass
	return count

@register.simple_tag
def totprice(object_list):
    total = 0
    for order in object_list:
        total += order.quantity*order.product.cost
    return total

@register.simple_tag
def address(userid):
    user=CartUser.objects.get(id=userid)
    return user.address
