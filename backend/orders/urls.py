# 订单模块 —— 路由配置
# 由 DRF 路由器自动生成订单与收货地址的增删改查路由，
# 视图集中的 @action 方法会一并生成子路径，最终挂载在 /api/orders/ 下。

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, AddressViewSet

# DefaultRouter 会自动为每个视图集生成列表与详情路由，视图集中的 @action 方法也会生成对应子路径
router = DefaultRouter()
# 订单：/api/orders/、/api/orders/{id}/ 以及 buy_product、pay、audit 等自定义动作
router.register('orders', OrderViewSet, basename='order')
# 收货地址：/api/orders/addresses/、/api/orders/addresses/{id}/
router.register('addresses', AddressViewSet, basename='address')

urlpatterns = [
    # 将路由器生成的所有路由统一交给上层 config/urls.py 的 api/orders/ 前缀
    path('', include(router.urls)),
]
