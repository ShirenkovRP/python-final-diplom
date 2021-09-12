from django.contrib import admin

# Register your models here.
from order_app.models import Order, OrderItem


admin.site.register(Order)
admin.site.register(OrderItem)
