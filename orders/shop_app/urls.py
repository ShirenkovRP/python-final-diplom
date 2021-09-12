from django.urls import path, include
from rest_framework.routers import DefaultRouter

from shop_app.views import CategoryView, ShopView, ProductInfoViewSet, PartnerState, PartnerUpdate


app_name = 'shop_app'
router = DefaultRouter()
router.register(r'products', ProductInfoViewSet, basename='products')
router.register(r'categories', CategoryView, basename='categories')
router.register(r'shops', ShopView, basename='shops')

urlpatterns = [
    # path('categories', CategoryView.as_view(), name='categories'),
    # path('shops', ShopView.as_view(), name='shops'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('', include(router.urls)),
]
