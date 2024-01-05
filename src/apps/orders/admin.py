from django.contrib import admin
from src.apps.orders.models import Cart, CartItem, Order, OrderItem, Coupon

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
