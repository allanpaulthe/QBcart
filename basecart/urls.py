from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='QBcart API')

api_routes = [
	path('',schema_view,name='schema'),
	path('login/',views.login, name='apilogin'),
	path('product/',views.ProductListOrCreate.as_view(), name='product'),
	path('product/<int:pk>/',views.ProductDetail.as_view(), name='productitem'),
	path('cart/',views.CartListOrCreate.as_view(), name='cart'),
	path('cart/<int:pk>/',views.CartDetail.as_view(), name='cartitem'),
	path('order/',views.OrderListOrCreate.as_view(), name='order'),
	path('order/<int:pk>/',views.OrderDetail.as_view(), name='orderitem'),
]

urlpatterns=[
	path('', views.IndexView.as_view(), name = 'index'),
	path('login/', auth_views.login, name = 'login'),
	path('logout/', auth_views.logout, name = 'logout'),
	path('signup/', views.SignUpView.as_view(), name = 'signup'),
	path('myproducts/',views.MyProductsView.as_view(),name='myproducts'),
	path('addproduct/', views.AddProductView.as_view(), name = 'addproduct'),
	path('productdetail/<int:pk>/', views.ProductDetailView.as_view(), name = 'productdetail'),
	path('productedit/<int:pk>/', views.ProductEditView.as_view(), name = 'productedit'),
	path('viewcart/',views.CartDetailView.as_view(), name='viewcart'),
	path('vieworder/',views.ViewOrder.as_view(), name='vieworder'),
	path('placeorder/',views.CreateOrder.as_view(), name='placeorder'),
	path('api/', include(api_routes),name='api'),
	# admin page urls
	# cart User
	path('cartuseradmin/', views.CartUserAdmin.as_view(),name='cartuseradmin'),
	path('cartusercreateadmin/', views.CartUserCreateAdmin.as_view(),name='cartusercreateadmin'),
	path('cartusereditadmin/<int:pk>/', views.CartUserEditAdmin.as_view(),name='cartusereditadmin'),
	# product
	path('productadmin/', views.ProductAdmin.as_view(),name='productadmin'),
	path('productcreateadmin/', views.ProductCreateAdmin.as_view(),name='productcreateadmin'),
	path('producteditadmin/<int:pk>/', views.ProductEditAdmin.as_view(),name='producteditadmin'),
	# Cart
	path('cartadmin/', views.CartAdmin.as_view(),name='cartadmin'),
	path('cartcreateadmin/', views.CartCreateAdmin.as_view(),name='cartcreateadmin'),
	path('carteditadmin/<int:pk>/', views.CartEditAdmin.as_view(),name='carteditadmin'),
	# Order
	path('orderadmin/', views.OrderAdmin.as_view(),name='orderadmin'),
	path('ordercreateadmin/', views.OrderCreateAdmin.as_view(),name='ordercreateadmin'),
	path('ordereditadmin/<int:pk>/', views.OrderEditAdmin.as_view(),name='ordereditadmin'),
	# Activitylog
	path('activityadmin/', views.CartActivityLoggerAdmin.as_view(),name='activityadmin'),
	path('activitycreateadmin/', views.CartActivityLoggerCreateAdmin.as_view(),name='activitycreateadmin'),
	path('activityeditadmin/<int:pk>/', views.CartActivityLoggerEditAdmin.as_view(),name='activityeditadmin'),
	#period update
	path('viewperiod/',views.PeriodAdmin.as_view(),name='viewperiod'),
	path('setperiod/<int:pk>/',views.PeriodEditAdmin.as_view(),name='setperiod'),
]