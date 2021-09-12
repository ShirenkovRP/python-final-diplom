from django.contrib import admin

# Register your models here.
from shop_app.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductInfo)
admin.site.register(Parameter)
admin.site.register(ProductParameter)
