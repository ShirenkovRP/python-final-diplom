from django.urls import path

from order_app.views import OrderView, PartnerOrders, BasketView


app_name = 'order_app'

urlpatterns = [
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('order', OrderView.as_view(), name='order'),
    path('basket', BasketView.as_view(), name='basket'),
    ]